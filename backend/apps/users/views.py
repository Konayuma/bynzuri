from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import constant_time_compare
from rest_framework.throttling import AnonRateThrottle
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import UserSerializer, RegisterSerializer, AddressSerializer, SupportInquirySerializer
from .models import User, Address, EmailVerification, PasswordResetRequest
from .password_reset import issue_password_reset, token_generator, RESEND_DELAY as PASSWORD_RESET_DELAY
from .verification import issue_code, code_for, RESEND_DELAY, MAX_ATTEMPTS


class VerificationThrottle(AnonRateThrottle):
    scope = 'email_verification'


class PasswordResetThrottle(AnonRateThrottle):
    scope = 'password_reset'


class SupportInquiryThrottle(AnonRateThrottle):
    scope = 'support_inquiry'


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            user = serializer.save()
            issue_code(user)

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by('-is_default', '-created_at', 'id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class ForgotPasswordView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [PasswordResetThrottle]

    def post(self, request):
        email = str(request.data.get('email', '')).strip().lower()
        if not email:
            return Response(
                {'detail': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            user = User.objects.select_for_update().filter(email__iexact=email, is_active=True).first()
            if user:
                existing = PasswordResetRequest.objects.select_for_update().filter(user=user).first()
                if not existing or timezone.now() >= existing.sent_requested_at + PASSWORD_RESET_DELAY:
                    issue_password_reset(user)

        return Response(
            {'detail': 'If an account with that email exists, a reset link has been sent.'},
            status=status.HTTP_200_OK
        )


class ResetPasswordView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uid = request.data.get('uid', '')
        token = request.data.get('token', '')
        new_password = request.data.get('new_password', '')

        if not all([uid, token, new_password]):
            return Response(
                {'detail': 'UID, token, and new_password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(new_password) < 8:
            return Response(
                {'detail': 'Password must be at least 8 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id, is_active=True)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {'detail': 'Invalid reset link'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not token_generator.check_token(user, token):
            return Response(
                {'detail': 'Reset link is invalid or has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            user.set_password(new_password)
            user.save(update_fields=['password'])
            PasswordResetRequest.objects.filter(user=user).exclude(status='expired').update(status='expired')

        return Response(
            {'detail': 'Password has been reset successfully'},
            status=status.HTTP_200_OK
        )


class SupportInquiryCreateView(generics.GenericAPIView):
    serializer_class = SupportInquirySerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [SupportInquiryThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        honeypot = serializer.validated_data.pop('website', '').strip()
        if honeypot:
            return Response(
                {
                    'detail': 'Your inquiry has been received. Our team will reply by email.',
                    'reference': 'SUP-RECEIVED',
                },
                status=status.HTTP_201_CREATED,
            )

        user = request.user if getattr(request.user, 'is_authenticated', False) else None
        inquiry = serializer.save(user=user)
        return Response(
            {
                'id': str(inquiry.id),
                'reference': inquiry.reference,
                'detail': 'Your inquiry has been received. Our team will reply by email.',
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [VerificationThrottle]

    def post(self, request):
        email = str(request.data.get('email', '')).strip().lower()
        code = str(request.data.get('code', '')).strip()
        message = 'This code is incorrect or expired. Check it or request a new code.'
        if not email or len(code) != 6 or not code.isascii() or not code.isdigit():
            return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            user = User.objects.select_for_update().filter(email__iexact=email).first()
            challenge = EmailVerification.objects.select_for_update().filter(user=user).first() if user else None
            if not challenge or challenge.user.email_verified or challenge.user.is_active or challenge.expires_at <= timezone.now() or challenge.attempts >= MAX_ATTEMPTS:
                return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)
            challenge.attempts += 1
            if not constant_time_compare(code_for(challenge), code):
                challenge.save(update_fields=['attempts'])
                return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)
            user.email_verified = True
            user.is_active = True
            user.email_verification_token = ''
            user.save(update_fields=['email_verified', 'is_active', 'email_verification_token'])
            challenge.status = 'verified'
            challenge.save(update_fields=['status', 'attempts'])
        return Response({'detail': 'Email verified. You can now sign in.'})

    def get(self, request):
        token = request.query_params.get('token', '')
        if not token:
            return Response(
                {'detail': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email_verification_token=token)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Invalid verification token'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.email_verified:
            return Response(
                {'detail': 'Email already verified'},
                status=status.HTTP_200_OK
            )

        user.email_verified = True
        user.email_verification_token = ''
        user.save(update_fields=['email_verified', 'email_verification_token'])

        return Response(
            {'detail': 'Email verified successfully'},
            status=status.HTTP_200_OK
        )


class ResendVerificationEmailView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [VerificationThrottle]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response(
                {'detail': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            user = User.objects.select_for_update().filter(email__iexact=email).first()
            challenge = EmailVerification.objects.select_for_update().filter(user=user).first() if user else None
            if user and challenge and not user.email_verified and not user.is_active and timezone.now() >= challenge.sent_requested_at + RESEND_DELAY:
                issue_code(user)
        return Response({'detail': 'If this account is eligible, a new code will be emailed. Please wait at least one minute between requests.'})
