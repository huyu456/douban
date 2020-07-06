from datetime import datetime, timedelta

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from douban.settings import BASE_URL
from .customExection import CustomExection
from .models import UserModel, CodeModel


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['username', 'gender', 'birthday', 'add_time', 'email', 'profile_photo']
        read_only_fields = ['username', 'add_time']  # 只读字段不可修改

    def validate(self, attrs):
        email = attrs.get('email')
        if email and email != self.instance.email:
            raise CustomExection(detail='邮箱修改需要验证码(这只是测试)', error_code=10006)
        return attrs


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True, label='用户名')
    email = serializers.EmailField(label='邮箱')
    code = serializers.CharField(label='验证码', max_length=6, write_only=True)
    password = serializers.CharField(
        style={'input_type': 'password'}, label="密码", write_only=True,
    )

    def validate(self, attrs):
        code = attrs.pop('code')
        email = attrs['email']
        if len(code) != 6:
            raise serializers.ValidationError("验证码不规范")
        code_info = get_object_or_404(CodeModel, code=code, email=email, email_type='register')
        if code_info:
            if (datetime.now() - code_info.add_time).seconds > 60:
                raise CustomExection(detail="验证码过期", error_code=20003)
        return attrs

    def create(self, validated_data):
        if UserModel.objects.filter(Q(username=validated_data['username']) | Q(email=validated_data['email'])):
            raise serializers.ValidationError("用户或邮箱已存在")
        return UserModel.objects.create(**validated_data)


class ForgetPassword(serializers.Serializer):
    # write_only = True,创建或修改成功后，前端不会返回该字段
    email = serializers.EmailField(label='邮箱', write_only=True)
    password = serializers.CharField(
        style={'input_type': 'password'}, label="密码", write_only=True,
    )
    new_password = serializers.CharField(
        style={'input_type': 'password'}, label="新密码", write_only=True,
    )
    new_password2 = serializers.CharField(
        style={'input_type': 'password'}, label="确认新密码", write_only=True,
    )

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError(detail='两次密码不一致')
        if attrs['password'] == attrs['new_password']:
            raise serializers.ValidationError(detail='新密码与旧密码不能相同')
        return attrs

    def update(self, instance, validated_data):
        user = get_object_or_404(UserModel, email=validated_data['email'])
        if user.check_password(validated_data['password']):
            user.set_password(validated_data['new_password'])
            user.save()
            return user
        raise serializers.ValidationError(detail='请检查密码是否正确')


class EmailSerializer(serializers.Serializer):
    email = serializers.CharField(label='邮箱', required=True)
    email_type = serializers.ChoiceField(choices=(('register', '注册'), ('change_pwd', '修改密码'), ('login', '登录')))

    def validate(self, attrs):
        email = attrs['email']
        email_type = attrs['email_type']
        if email_type == 'register':
            if UserModel.objects.filter(email=email).count():
                raise CustomExection(detail="用户已注册", error_code=20001)
        elif email_type == 'change_pwd' or email_type == 'login':
            if UserModel.objects.filter(email=email).count() == 0:
                raise CustomExection(detail='用户未注册')
        else:
            raise CustomExection(detail="不存在的类型")
        # 验证码发送频率
        one_mintes_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if CodeModel.objects.filter(add_time__gt=one_mintes_ago, email=email).count():
            raise serializers.ValidationError("距离上一次发送未超过60s")
        return attrs


# 自定义jwt serializer
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user, *args, **kwargs):
        token = super().get_token(user)
        token['name'] = user.username
        token['profile_photo'] = BASE_URL + user.profile_photo.url
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data
