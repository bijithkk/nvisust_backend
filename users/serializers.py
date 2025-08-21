from typing import Any
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Role


User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.SlugRelatedField(slug_field="name", queryset=Role.objects.all(), required=False, allow_null=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "password", "role"]
        extra_kwargs = {
            "username": {"required": False, "allow_blank": True, "validators": []},
        }

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        email = attrs.get('email')
        if email:
            email_lower = email.lower()
            if User.objects.filter(email__iexact=email_lower).exists():
                raise serializers.ValidationError({
                    'email': 'Email already in use'
                })
            attrs['email'] = email_lower
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        password = validated_data.pop("password")
        request = self.context.get('request')
        desired_role = validated_data.pop('role', None)

        # Default role to EMPLOYEE unless an authenticated admin is creating the user
        role_to_set = None
        if request and request.user and request.user.is_authenticated and getattr(request.user, 'is_admin', False):
            role_to_set = desired_role
        if role_to_set is None:
            role_to_set, _ = Role.objects.get_or_create(name=Role.EMPLOYEE)

        user = User(**validated_data)
        user.role = role_to_set
        user.set_password(password)
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    role = RoleSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role"]


class ProfileSerializer(serializers.ModelSerializer):
    role = RoleSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role", "date_joined"]


class UserUpdateSerializer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField(slug_field="name", queryset=Role.objects.all(), required=False, allow_null=True)
    password = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "role", "password"]
        extra_kwargs = {
            "username": {"required": False, "allow_blank": True, "validators": []},
        }

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        email = attrs.get('email')
        if email:
            email_lower = email.lower()
            # Exclude current instance when checking for duplicates
            qs = User.objects.filter(email__iexact=email_lower)
            if self.instance is not None:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    'email': 'Email already in use'
                })
            attrs['email'] = email_lower
        return attrs

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role.name if getattr(user, 'role', None) else None
        return token

    def validate(self, attrs):
        if 'email' in attrs and isinstance(attrs['email'], str):
            attrs['email'] = attrs['email'].lower()
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role.name if getattr(self.user, 'role', None) else None,
        }
        return data