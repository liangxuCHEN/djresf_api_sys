from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views import generic, csrf

from rest_framework import viewsets,mixins,generics,permissions, status
from rest_framework.response import Response

from media_sys.models import WXuser, QiniuMedia, Message
from media_sys.serializers import WxUserSerializer, QiniuMediaSerializer, MessageSerializer, MessageSerializer_json
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
    |-openid: 微信openid
    |-name: 用户名
    |-phone:手机号码
    """
    queryset = WXuser.objects.all().order_by('-created')
    serializer_class = WxUserSerializer
    permission_classes = (IsAdminOrReadOnly,)
    # 用什么作为唯一设别
    #lookup_field = 'openid'
    # 使用 title 作为另一个筛选条件
    #filter_fields = ['name']
    filter_class =WXuserFilter

    def create(self, request):
        openid = request.POST.get('openid')
        user = WXuser.objects.filter(openid=openid)
        if len(user) > 0:
            res = {'message': '用户已经存在', 'is_error': True}
            return HttpResponse(json.dumps(res), content_type="application/json")
        else:
            user = WXuser(
                openid=openid,
                name=request.POST.get('name'),
                phone=request.POST.get('phone'),
            )
            user.save()
            serialize = WxUserSerializer(user, context={'request': request})
            return Response(serialize.data, status=status.HTTP_201_CREATED)



class QiniuMediaViewSet(viewsets.ModelViewSet):
    """
    七牛多媒体保存
    |-name: 图片名称
    |-key: 七牛上的名称
    |-qn_url: 完整图片地址(不用输入)
    |-image: 上传图片文件，上传成功后会变成本地访问的地址，但不开放访问
    |-created: 创建时间
    
    上传单张图片参数
    data = {name, key, image}
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
    #lookup_field = 'user_openid'

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
    用户评论记录：
    |--openid:微信用户openid, 
    |--pics:图片链接，多余一张用　‘+’ 隔开
    |--content: 评论内容
    |--data = {openid: 'xxxxx', pics: 'pic1_url+pic2_url+... ', content: ''}

    """
    queryset = Message.objects.all().order_by('-created')
    serializer_class = MessageSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_fields = ['user']


    def create(self, request):
        user = request.POST.get('user')
        if 'http' in user:
            user_id = user.split('/')[-2]
            user = WXuser.objects.get(pk=user_id)
            msg = Message(
                user=user,
                content=request.POST.get('content'),
                pics=request.POST.get('pics'),
            )
            msg.save()
            serialize = MessageSerializer(msg, context={'request': request})
            return Response(serialize.data, status=status.HTTP_201_CREATED)
        else:

            try:
                user = WXuser.objects.filter(openid=request.POST.get('user')).first()
                if user:
                    msg = Message(
                        user=user,
                        content=request.POST.get('content'),
                        pics=request.POST.get('pics'),
                    )
                    msg.save()
                    serialize = MessageSerializer_json(msg)
                    res = {'message': '保存成功', 'msg': serialize.data, 'is_error': False}
                else:
                    res = {'message': "没有此用户", 'is_error': True}
            except Exception as e:
                res = {'message': e, 'is_error': True}

        return Response(json.dumps(res))