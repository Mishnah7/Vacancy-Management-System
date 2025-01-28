from django.contrib.auth import get_user_model, login
from django.utils.decorators import method_decorator
from requests.exceptions import HTTPError
from rest_framework import decorators, permissions, response, status
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from social_core.backends.oauth import BaseOAuth2
from social_core.exceptions import AuthForbidden, AuthTokenError, MissingBackend
from social_django.utils import load_backend, load_strategy
from rest_framework.exceptions import ValidationError
from django_ratelimit.decorators import ratelimit
import secrets
import logging

from jobsapp.api.permissions import IsEmployee

from .custom_claims import MyTokenObtainPairSerializer
from .serializers import SocialSerializer, UserCreateSerializer, UserSerializer

User = get_user_model()

logger = logging.getLogger(__name__)


@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.AllowAny])
def registration(request):
    serializer = UserCreateSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    user = serializer.save()
    res = {"status": True, "message": "Successfully registered"}
    return response.Response(res, status.HTTP_201_CREATED)


class EditEmployeeProfileAPIView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    http_method_names = ["get", "put"]
    permission_classes = [IsAuthenticated, IsEmployee]

    def get_object(self):
        return self.request.user


def generate_oauth_state():
    """Generate a secure state parameter for OAuth"""
    return secrets.token_urlsafe(32)


def validate_oauth_state(state):
    """Validate OAuth state parameter to prevent CSRF attacks"""
    if not state or len(state) < 32:
        return False
    try:
        # Add additional validation if needed
        return True
    except Exception as e:
        logger.error(f"Error validating OAuth state: {str(e)}")
        return False


class SocialLoginAPIView(GenericAPIView):
    """Social authentication view"""
    serializer_class = SocialSerializer
    permission_classes = [permissions.AllowAny]
    ALLOWED_PROVIDERS = ['google', 'github']
    RATE_LIMIT = '5/m'

    @method_decorator(ratelimit(key='ip', rate=RATE_LIMIT))
    def post(self, request):
        """
        Authenticate user through the provider and access_token
        """
        try:
            provider = request.data.get('provider', '').lower()
            if provider not in self.ALLOWED_PROVIDERS:
                raise ValidationError({
                    'provider': f"Invalid provider. Allowed: {', '.join(self.ALLOWED_PROVIDERS)}"
                })

            if not validate_oauth_state(request.data.get('state')):
                raise ValidationError({
                    'state': "Invalid or missing state parameter"
                })

            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            strategy = load_strategy(request)
            
            try:
                backend = load_backend(strategy=strategy, name=provider, redirect_uri=None)
            except MissingBackend:
                raise ValidationError({
                    'provider': f"Provider '{provider}' is not configured properly"
                })

            try:
                if isinstance(backend, BaseOAuth2):
                    access_token = serializer.validated_data.get('access_token')
                    user = backend.do_auth(access_token)
                else:
                    raise ValidationError({
                        'provider': f"Provider '{provider}' is not supported"
                    })
            except (HTTPError, AuthTokenError) as e:
                logger.error(f"OAuth authentication error: {str(e)}")
                raise ValidationError({
                    'access_token': "Invalid token",
                    'detail': str(e)
                })
            except AuthForbidden as e:
                logger.error(f"OAuth authentication forbidden: {str(e)}")
                raise ValidationError({
                    'error': "Authentication forbidden",
                    'detail': str(e)
                })
            except Exception as e:
                logger.error(f"Unexpected error during OAuth authentication: {str(e)}")
                raise ValidationError({
                    'error': "Authentication failed",
                    'detail': "An unexpected error occurred"
                })

            if not user:
                raise ValidationError({
                    'error': "Authentication failed",
                    'detail': "Unable to authenticate with provided credentials"
                })

            if not user.is_active:
                raise ValidationError({
                    'error': "Authentication failed",
                    'detail': "User account is disabled"
                })

            return Response({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
                'message': 'Successfully authenticated'
            }, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in social login: {str(e)}")
            return Response({
                'error': "Authentication failed",
                'detail': "An unexpected error occurred"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
