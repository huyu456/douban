from django.contrib import admin

from .models import UserModel, CodeModel


@admin.register(UserModel)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'gender', 'birthday', 'email', 'profile_photo')


@admin.register(CodeModel)
class CodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'email', 'email_type', 'add_time')
