from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, MyLoginView, LogoutView, UserListView, ProfileView, UserCreateView, UserDetailView


urlpatterns = [
    # path('register', RegisterView.as_view(), name='register'),
    path('login', MyLoginView.as_view(), name='login'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('users', UserListView.as_view(), name='users'),
    path('users/create', UserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>', UserDetailView.as_view(), name='user-detail'),
    path('profile', ProfileView.as_view(), name='profile'),
]