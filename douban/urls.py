"""douban URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from user.views import UserViewSet, ForgetPwdView, SendEmailView, MyTokenObtainPairView
from rest_framework.documentation import include_docs_urls

router = DefaultRouter()
router.register(r'api/users', UserViewSet, basename='user')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('docs/', include_docs_urls(title='豆瓣用户')),
    path('api-auth/', include('rest_framework.urls')),
    path('', include(router.urls)),
    path('api/forgot_password/', ForgetPwdView.as_view(), name='forgot_pwd'),
    path('api/send_email/', SendEmailView.as_view()),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
