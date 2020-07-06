from datetime import datetime

from django.contrib.auth.backends import ModelBackend
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, generics, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView

from .customExection import CustomExection
from .models import UserModel, CodeModel
from .serializers import UserSerializer, UserRegisterSerializer, ForgetPassword, \
    EmailSerializer, MyTokenObtainPairSerializer
from .utils import send_code_email, gen_code


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwars):
        try:
            user = UserModel.objects.get(Q(email=username) | Q(username=username))
        except UserModel.DoesNotExist:
            raise CustomExection('用户不存在', error_code=10004)
        else:
            if isinstance(request, WSGIRequest):
                code = request.POST.get('code')
            else:
                code = request.data.get('code')
            has_code = CodeModel.objects.filter(email=username, code=code)
            if code and has_code:
                code_query = CodeModel.objects.get(email=username, code=code)
                if (datetime.now() - code_query.add_time).seconds > 600:
                    raise CustomExection('验证码过期', error_code=10001)
                return user
            elif code and len(has_code) == 0:
                raise CustomExection('验证码错误', error_code=10002)
            if user.check_password(password):
                return user
            else:
                raise CustomExection('密码错误', error_code=10003)


class UserViewSet(viewsets.GenericViewSet,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.RetrieveModelMixin):
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    queryset = UserModel.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserSerializer
        elif self.action == 'create':
            return UserRegisterSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return []
        elif self.action == 'retrieve' or 'update':
            return [IsAuthenticated()]
        return []

    def get_object(self):
        # 当用户登录后，避免该用户访问到其他用户信息
        return self.request.user


class ForgetPwdView(generics.UpdateAPIView):
    serializer_class = ForgetPassword
    queryset = UserModel.objects.all()

    def get_object(self):
        return get_object_or_404(self.get_queryset(), email=self.request.data['email'])

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SendEmailView(generics.CreateAPIView):
    serializer_class = EmailSerializer

    def create(self, request, *args, **kwargs):
        code = gen_code()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = self.request.data['email']
        email_type = self.request.data['email_type']
        if email_type == 'register':
            email_title = '用户注册验证码'
        elif email_type == 'login':
            email_title = '用户登录验证码'
        else:
            email_title = '修改密码验证码'
        send_code_email(email, email_title, '您的验证码为{0},有效期为60s'.format(code))
        CodeModel.objects.create(email=email, code=code, email_type=email_type)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# 自定义JWT的View
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
