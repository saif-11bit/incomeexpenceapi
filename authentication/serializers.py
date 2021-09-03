from django.db import models
from rest_framework import serializers
from .models import User
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str,force_str,smart_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68,min_length=6,write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    
    def validate(self, attrs):
        email = attrs.get('email', '')

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=2000)

    class Meta:
        model = User
        fields = ['token']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=200)
    password = serializers.CharField(min_length=6, max_length=200,write_only=True)
    token = serializers.CharField(max_length=1000, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'token']

    
    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = auth.authenticate(email=email,password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials.Try again!')

        if not user.is_active:
            raise AuthenticationFailed('Account not active.Contact admin!')
        
        if not user.is_verified:
            raise AuthenticationFailed('Please Verify your email!')

        
        return {
            'email':user.email,
            'token':user.tokens,
        }


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=244)

    class Meta:
        fields = ['email']



class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6,max_length=100,write_only=True)
    token = serializers.CharField(min_length=2,max_length=1000,write_only=True)
    uidb64 = serializers.CharField(min_length=1,write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link invalid!',401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link invalid!',401)

        return super().validate(attrs)