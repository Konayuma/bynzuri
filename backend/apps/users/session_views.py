from django.conf import settings
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import permissions, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

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
