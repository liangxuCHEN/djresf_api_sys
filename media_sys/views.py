from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse,JsonResponse
#from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
#from django.views import generic, csrf

from rest_framework import viewsets,mixins,generics,permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from media_sys.models import WXuser, QiniuMedia, Message, QiniuZipModel
from media_sys.serializers import WxUserSerializer, QiniuMediaSerializer, MessageSerializer, \
    MessageSerializer_json, MessageMoreInfoSerializer, ZipInfoSerializer
from media_sys.filtesr import WXuserFilter, MessageFilter
from media_sys.permissions import IsAdminOrReadOnly
from media_sys.tools import Qiqiu, handle_uploaded_file

from api_sys import settings

import json
import uuid
import os
from datetime import datetime

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
    
    ../get_token: 用于获取上传验证，方便前端可以直接上传图片，不需要经过服务器
    
    ../upload_zip POST: 
    |--目前只支持zip压缩的文档，可以实现批量图片上传
    |--参数：{name:文档命名, key:七牛保存的路径前缀, zip:压缩文档}  
    
    ../zip: 查看上传结果
    """
    queryset = QiniuMedia.objects.all().order_by('-created')
    serializer_class = QiniuMediaSerializer
    permission_classes = (IsAdminOrReadOnly,)

    @action(detail=False)
    def get_token(self, request):
        """
        获取七牛上传认证
        :param request: 
        :return: 
        """
        qn = Qiqiu(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
        token = qn.get_token(settings.QINIU_BUCKET_NAME)
        return allow_all(JsonResponse({"token": token, 'domain': "http://%s" % settings.QINIU_BUCKET_DOMAIN}))

    @action(detail=False, methods=['POST'])
    def upload_zip(self, request):
        """
        name:文档命名
        zip: 是上传文档的名字
        key: 文件路径前缀
        
        :return: 上传结果记录
        """
        try:
            content = {'success': [], 'error': []}
            zip_name = "%s-%s.zip" % (request.POST.get('name','tmp'),str(uuid.uuid4())[:6])
            file_name = os.path.join(settings.MEDIA_ROOT, zip_name)
            files = handle_uploaded_file(request.FILES['zip'], file_name)
            # 上传七牛
            for f in files:
                qn = Qiqiu(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
                key = "%s/%s/%s/%s" % (
                    request.POST.get('key','tmp'),
                    datetime.today().strftime("%Y%m%d"),
                    zip_name,
                    f["name"]
                )
                r = qn.upload(settings.QINIU_BUCKET_NAME, key, f["path"])
                if r:
                    content['success'].append("http://%s/%s" % (settings.QINIU_BUCKET_DOMAIN, key))
                else:
                    content['error'].append("%s" % (key))

        except Exception as e:
            content = {"is_error": True, "message":e}

        finally:
            zip_model = QiniuZipModel(
                name=zip_name or 'undefinded',
                key=request.POST.get('key','tmp'),
                image_logs=json.dumps(content)
            )
            zip_model.save()

        content['is_error'] = False

        return allow_all(JsonResponse(content))

    @action(detail=False)
    def zip(self,request):
        """
        查看压缩包上传结果
        筛选数据
        id　精确查询
        name 可模糊查询
        key 可模糊查询
        """
        queryset = QiniuZipModel.objects.all()

        if request.GET.get('id'):
            queryset = queryset.filter(id=request.GET.get('id')).first()
            return Response(ZipInfoSerializer(queryset).data)

        if request.GET.get('name'):
            queryset = queryset.filter(name__contains=request.GET.get('name'))

        if request.GET.get('key'):
            queryset = queryset.filter(key__contains=request.GET.get('key'))

        queryset = queryset.order_by('-created')
        serializer = ZipInfoSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def find_pics(self, request):
        """
        查询图片
        参数：key
        例子：http://img.foshanplus.com/img/40years/content/90/93_102_86.png
        可以搜索: "img/40years/", "img/40years/content"，"img/40years/content/90” 
        """
        key = request.GET.get('key')
        qn = Qiqiu(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
        content = {'domain': settings.QINIU_BUCKET_DOMAIN}
        content['datas'] = qn.list_files(settings.QINIU_BUCKET_NAME,prefix=key)
        return allow_all(JsonResponse(content))


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
            return JsonResponse(res)



class MessageViewSet(viewsets.ModelViewSet):
    """
    用户评论记录：
    |--message_id　信息id
    |--user_id　用户id,可以通过　/wxuser/id 访问
    |--user_name 微信用户名字
    |--user_phone　微信用户电话
    |--pics:图片链接，多余一张用　‘+’ 隔开
    |--content: 评论内容
    |--data = {user: 'input user oponid', pics: 'pic1_url+pic2_url+... ', content: ''}

    """
    queryset = Message.objects.all().order_by('-created')
    serializer_class = MessageSerializer
    permission_classes = (IsAdminOrReadOnly,)
    #filter_fields = ['user']
    filter_class = MessageFilter

    def list(self, request):
        print(request.GET)
        queryset = Message.objects.all().order_by('-created')
        #过滤条件
        if request.GET.get('name'):
            queryset = queryset.filter(user__name__icontains=request.GET.get('name'))
        if request.GET.get('phone'):
            queryset = queryset.filter(user__phone__icontains=request.GET.get('phone'))
        serializer = MessageMoreInfoSerializer(queryset, many=True)
        return Response(serializer.data)

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





