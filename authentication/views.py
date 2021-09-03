from datetime import date
from django.core.mail import message
from django.http import response
from django.shortcuts import render
from django.utils.encoding import smart_bytes, smart_str,DjangoUnicodeDecodeError
from rest_framework import generics, serializers,status
from .serializers import (RegisterSerializer,EmailVerificationSerializer,LoginSerializer,ResetPasswordSerializer,SetNewPasswordSerializer)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .renderers import UserRenderer
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class RegisterView(generics.GenericAPIView):
    
    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer,)

    def post(self,request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data

        user = User.objects.get(email=user_data['email'])

        token = RefreshToken.for_user(user).access_token

        current_site = get_current_site(request).domain
        relativeLink = reverse('email-verify')

        absurl = 'http://' + current_site + relativeLink + "?token=" + str(token)

        email_body = "Hi "+user.email + " Use the below link to verify your email\n"+absurl
        data = {
            'to_email':user.email,
            'email_body':email_body,
            'email_subject':"Verify your email!!"
        }
        Util.send_email(data)

        return Response(user_data,status=status.HTTP_201_CREATED)


class VerifyEmail(APIView):
    
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter('token',in_=openapi.IN_QUERY,description='Description',type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self,request):
        token = request.GET.get('token')
        # print(token)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY,algorithms=['HS256'])
            # print(payload)
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'email':'Successfully activated'},status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError as identifier:
            return Response({'error':'Activation expired!'},status=status.HTTP_400_BAD_REQUEST)

        except jwt.exceptions.DecodeError as identifier:
            return Response({'error':'Invalid Token!'},status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):

    serializer_class = LoginSerializer

    def post(self, request):

        user = request.data
        
        serilaizer = self.serializer_class(data=user)
        serilaizer.is_valid(raise_exception=True)

        return Response(serilaizer.data, status=status.HTTP_200_OK)


class ResetPasswordView(generics.GenericAPIView):
    
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        email = request.data['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relativeLink = reverse('confirm-password-reset',kwargs={'uidb64':uidb64,'token':token})
            absurl = 'http://' + current_site + relativeLink
            email_body = "Hello,\n Use the below link to reset your password\n"+absurl
            data = {
                'to_email':email,
                'email_body':email_body,
                'email_subject':"Reset your password!!"
            }
            Util.send_email(data)

        return Response({'success':'Email has been sent with password reset link!'}, status=status.HTTP_200_OK)


class PasswordTokenCheckApi(generics.GenericAPIView):

    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user,token=token):
                return Response({'error':'Link not valid, please request a new one!'}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({'success':True, 'message':'Credentials valid!', 'uidb64':uidb64, 'token':token}, status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as identifier:
                return Response({'error':'Link not valid, please request a new one!'}, status=status.HTTP_401_UNAUTHORIZED)


class SetNewPasswordApiView(generics.GenericAPIView):

    serializer_class = SetNewPasswordSerializer

    def patch(self,request):
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({'success':True, 'message':'password successfully reset!'}, status=status.HTTP_200_OK)