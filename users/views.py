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


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'refresh token required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({'detail': 'invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class UserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [AdminOrManagerCanList]

    def get_queryset(self):
        user = self.request.user
        qs = User.objects.select_related('role').all()
        if getattr(user, 'is_manager', False) and not getattr(user, 'is_admin', False):
            admin_role = Role.objects.filter(name=Role.ADMIN).first()
            if admin_role:
                qs = qs.exclude(role=admin_role)
        return qs


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


class ProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user

# Create your views here.
