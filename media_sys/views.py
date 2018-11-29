from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views import generic, csrf

from rest_framework import viewsets,mixins,generics,permissions

from media_sys.models import WXuser, QiniuMedia, Message
from media_sys.serializers import WxUserSerializer, QiniuMediaSerializer, MessageSerializer
from media_sys.filtesr import WXuserFilter
from media_sys.permissions import IsAdminOrReadOnly
import json

# Create your views here.

def allow_all(response):
    """
    解决跨域的问题
    :param response:
    :return:
    """
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response


def home_page(request):
    return render(request, 'index.html')



class WxUserList(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    """
    微信用户登记
    """
    queryset = WXuser.objects.all().order_by('-created')
    serializer_class = WxUserSerializer

    def get(self, request, *args, **kwargs):
        print('request', request.GET)
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        #request.POST.get('openid')
        print('request', request.POST)
        return self.create(request, *args, **kwargs)

class WxUserDetail(generics.RetrieveAPIView):
    queryset = WXuser.objects.all()
    serializer_class = WxUserSerializer


class WxUserViewSet(viewsets.ModelViewSet):
    """
    微信用户记录.
    """
    queryset = WXuser.objects.all().order_by('-created')
    serializer_class = WxUserSerializer
    permission_classes = (IsAdminOrReadOnly,)
    # 使用 title 作为另一个筛选条件
    #filter_fields = ['name']
    filter_class =WXuserFilter


class QiniuMediaViewSet(viewsets.ModelViewSet):
    """
    七牛多媒体保存
    """
    queryset = QiniuMedia.objects.all().order_by('-created')
    serializer_class = QiniuMediaSerializer
    permission_classes = (IsAdminOrReadOnly,)


class MessageList(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    """
    微信用户登记
    """
    queryset = Message.objects.all().order_by('-created')
    serializer_class = MessageSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = request.POST.get('user')
        if 'http' in user:
            return self.create(request, *args, **kwargs)
        else:

            try:
                user =  WXuser.objects.filter(openid=request.POST.get('user')).first()
                if user:
                    msg = Message(
                        user=user,
                        content=request.POST.get('content'),
                        pics=request.POST.get('pics'),
                    )
                    msg.save()
                    res = {'message': '保存成功', 'msg': msg.id, 'is_error': False}
                else:
                    res = {'message': "没有此用户", 'is_error': True}
            except Exception as e:
                res = {'message': e, 'is_error': True}
            return HttpResponse(json.dumps(res), content_type="application/json")



class MessageViewSet(viewsets.ModelViewSet):
    """
    用户评论.
    """
    queryset = Message.objects.all().order_by('-created')
    serializer_class = MessageSerializer
    filter_fields = ['user']