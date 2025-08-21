from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import MyTokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, UserListSerializer, ProfileSerializer, UserUpdateSerializer
from .permissions import AdminOrManagerCanList, IsAdmin, AdminCanViewAllOrManagerCanViewEmployee
from .models import Role


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MyLoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as exc:
            detail = getattr(exc, 'detail', None)
            if detail is None:
                detail_text = 'Invalid credentials'
            else:
                try:
                    detail_text = str(detail)
                except Exception:
                    detail_text = 'Invalid credentials'
            return Response({'message': 'Invalid email or password', 'detail': detail_text}, status=status.HTTP_401_UNAUTHORIZED)

        data = serializer.validated_data
        data['message'] = 'Login successful'
        return Response(data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'message': 'refresh token required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({'message': 'invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'logout successfully'}, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [AdminOrManagerCanList]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'is_manager', False) and not getattr(user, 'is_admin', False):
            # Managers should see only employees
            return User.objects.select_related('role').filter(role__name=Role.EMPLOYEE)
        if getattr(user, 'is_admin', False):
            # Admins should see managers and employees only (no admins)
            return User.objects.select_related('role').filter(role__name__in=[Role.MANAGER, Role.EMPLOYEE])
        return User.objects.none()


class UserCreateView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsAdmin]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.select_related('role').all()
    permission_classes = [AdminCanViewAllOrManagerCanViewEmployee]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return ProfileSerializer

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        try:
            data = response.data
            return Response({'message': 'User updated successfully', 'user': data}, status=response.status_code)
        except Exception:
            return response


class ProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user

# Create your views here.
