import time
import requests
from django.conf import settings
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.db import transaction
from django.middleware.csrf import get_token
from django.utils.crypto import constant_time_compare
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import permissions, status, views
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import EmailVerification, User
from .views import SIGNUP_PASSWORD_MAX_AGE, SIGNUP_PASSWORD_SALT

COOKIE = 'bynzuri_refresh'
COOKIE_PATH = '/api/auth/'


def set_refresh(response, token):
    response.set_cookie(COOKIE, token, max_age=int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
                        httponly=True, secure=settings.SESSION_COOKIE_SECURE,
                        samesite='None' if settings.SESSION_COOKIE_SECURE else 'Lax', path=COOKIE_PATH)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CsrfView(views.APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({'csrfToken': get_token(request)})


@method_decorator(csrf_protect, name='dispatch')
class CookieTokenView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            set_refresh(response, response.data.pop('refresh'))
        return response


@method_decorator(csrf_protect, name='dispatch')
class CookieRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        token = request.COOKIES.get(COOKIE)
        if not token:
            return Response({'detail': 'Session expired.'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(data={'refresh': token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as error:
            raise InvalidToken(error.args[0]) from error
        data = dict(serializer.validated_data)
        rotated = data.pop('refresh', None)
        response = Response(data)
        if rotated:
            set_refresh(response, rotated)
        return response


@method_decorator(csrf_protect, name='dispatch')
class LogoutView(views.APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.COOKIES.get(COOKIE)
        if token:
            try:
                RefreshToken(token).blacklist()
            except TokenError:
                pass
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(COOKIE, path=COOKIE_PATH, samesite='None' if settings.SESSION_COOKIE_SECURE else 'Lax')
        return response


def issue_session_response(user):
    refresh = RefreshToken.for_user(user)
    response = Response({'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
    set_refresh(response, str(refresh))
    return response


@method_decorator(csrf_protect, name='dispatch')
class CompleteSignupView(views.APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        setup_token = str(request.data.get('setup_token', '')).strip()
        password = str(request.data.get('password', ''))
        if not setup_token or not password:
            return Response({'detail': 'Setup token and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        if len(password) < 8 or not any(ch.isalpha() for ch in password) or not any(ch.isdigit() for ch in password):
            return Response({'detail': 'Password must be at least 8 characters and include a letter and a number.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            payload = TimestampSigner(salt=SIGNUP_PASSWORD_SALT).unsign(setup_token, max_age=SIGNUP_PASSWORD_MAX_AGE)
            user_id, nonce = payload.split(':', 1)
        except (BadSignature, SignatureExpired, ValueError):
            return Response({'detail': 'Your verification session has expired. Request a new code to continue.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            user = User.objects.select_for_update().filter(pk=user_id).first()
            challenge = EmailVerification.objects.select_for_update().filter(user=user).first() if user else None
            if (
                not user
                or not challenge
                or user.is_active
                or not user.email_verified
                or user.has_usable_password()
                or challenge.status != 'verified'
                or not constant_time_compare(challenge.nonce, nonce)
            ):
                return Response({'detail': 'Your verification session has expired. Request a new code to continue.'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(password)
            user.is_active = True
            user.save(update_fields=['password', 'is_active'])

        return issue_session_response(user)


def verify_google_id_token(credential: str) -> dict | None:
    client_id = settings.GOOGLE_CLIENT_ID
    if not client_id or not credential:
        return None
    try:
        resp = requests.get(
            'https://oauth2.googleapis.com/tokeninfo',
            params={'id_token': credential},
            timeout=10,
        )
    except requests.RequestException:
        return None
    if not resp.ok:
        return None
    try:
        data = resp.json()
    except ValueError:
        return None
    if data.get('aud') != client_id:
        return None
    if data.get('iss') not in ('accounts.google.com', 'https://accounts.google.com'):
        return None
    if str(data.get('email_verified', '')).lower() != 'true':
        return None
    email = str(data.get('email', '')).strip().lower()
    if not email:
        return None
    try:
        exp = int(data.get('exp', 0))
    except (TypeError, ValueError):
        return None
    if exp <= int(time.time()):
        return None
    return {
        'email': email,
        'first_name': str(data.get('given_name', '')).strip()[:150],
        'last_name': str(data.get('family_name', '')).strip()[:150],
    }


@method_decorator(csrf_protect, name='dispatch')
class GoogleAuthView(views.APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        if not settings.GOOGLE_CLIENT_ID:
            return Response({'detail': 'Google sign-in is not configured.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        credential = str(request.data.get('credential', '')).strip()
        profile = verify_google_id_token(credential)
        if not profile:
            return Response({'detail': 'Google sign-in could not be verified. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)

        email = profile['email']
        with transaction.atomic():
            user = User.objects.select_for_update().filter(email__iexact=email).first()
            if user is not None:
                if user.email_verified and user.has_usable_password() and not user.is_active:
                    return Response({'detail': 'This account is inactive.'}, status=status.HTTP_403_FORBIDDEN)
                updated_fields = []
                if not user.email_verified:
                    user.email_verified = True
                    updated_fields.append('email_verified')
                if not user.is_active:
                    user.is_active = True
                    updated_fields.append('is_active')
                if not user.first_name and profile['first_name']:
                    user.first_name = profile['first_name']
                    updated_fields.append('first_name')
                if not user.last_name and profile['last_name']:
                    user.last_name = profile['last_name']
                    updated_fields.append('last_name')
                if updated_fields:
                    user.save(update_fields=updated_fields)
            else:
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=None,
                    first_name=profile['first_name'],
                    last_name=profile['last_name'],
                    email_verified=True,
                    is_active=True,
                )
                user.set_unusable_password()
                user.save(update_fields=['password'])

        return issue_session_response(user)
