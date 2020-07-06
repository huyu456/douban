from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


class UserModel(AbstractUser):
    email = models.EmailField(verbose_name='邮箱', blank=True, null=True, default='')
    gender = models.CharField(choices=(('male', '男'), ('female', '女')), default='male',
                              max_length=10, verbose_name='性别')
    profile_photo = models.ImageField(verbose_name='头像', upload_to='%Y/%m/%d', default='user_normal.jpg')
    birthday = models.DateField(verbose_name='出生年月', blank=True, null=True)
    add_time = models.DateTimeField(verbose_name='注册时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = '用户管理'
        verbose_name = verbose_name_plural

    def __str__(self):
        return self.username


class CodeModel(models.Model):
    email = models.EmailField(verbose_name='邮箱')
    code = models.CharField(max_length=6, verbose_name='验证码')
    email_type = models.CharField(choices=(('register', '注册'),
                                           ('login', '登录'),
                                           ('change_pwd', '修改密码')), max_length=10)
    add_time = models.DateTimeField(verbose_name='发送时间', default=now)

    class Meta:
        verbose_name_plural = '验证码管理'
        verbose_name = verbose_name_plural
        ordering = ['-add_time']

    def __str__(self):
        return self.code

