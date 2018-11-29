from rest_framework import serializers
from media_sys.models import WXuser, Message, QiniuPic


class WxUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WXuser
        fields = ('openid', 'name', 'phone')


class QiniuPicSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = QiniuPic
        fields = ('key', 'created')


class MessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Message
        fields = ('user', 'content', 'pics', 'created')