"""api_sys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path
from django.conf.urls import url, include
from media_sys import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'wxusers', views.WxUserViewSet)
router.register(r'qnpic', views.QiniuMediaViewSet)
router.register(r'message', views.MessageViewSet)
#router.register(r'v2_message', views.MessageList)


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^home$', views.home_page, name='home_page'),
    url(r'^api/', include('rest_framework.urls', namespace='rest_framework')),
    #path('v2/wxusers/', views.WxUserList.as_view()),
    #path('wxusers/<int:pk>/', views.WxUserDetail.as_view()),

    #path('v2/message/', views.MessageList.as_view()),
]

urlpatterns += staticfiles_urlpatterns()