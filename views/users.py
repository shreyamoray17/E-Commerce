from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from serializers.users import UserRegistrationSerializer, UserProfileSerializer, LogoutSerializer
from django.core.cache import cache

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


@swagger_auto_schema(
    method='patch',
    request_body=UserProfileSerializer,
    responses={
        200: UserProfileSerializer,
        400: 'Bad Request - Validation error'
    },
    operation_description="Update user profile (partial update allowed - send only fields you want to change)"
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """
    Update user profile (partial update)
    
    Request body (update any field):
    {
        "first_name": "New Name",
        "last_name": "New Last Name",
        "phone_number": "9999999999"
    }
    """
    serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=LogoutSerializer,
    responses={
        200: 'Logged out successfully',
        400: 'Bad Request - Invalid token'
    },
    operation_description="Logout user by blacklisting the refresh token"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout user by blacklisting refresh token
    
    Request body:
    {
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        # Clear user cache if exists
        cache_key = f'user_session_{request.user.id}'
        cache.delete(cache_key)
        
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
