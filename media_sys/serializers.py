from rest_framework import serializers
from media_sys.models import WXuser, Message, QiniuMedia


class WxUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WXuser
        fields = ('openid', 'name', 'phone')


class QiniuMediaSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = QiniuMedia
        fields = ('name', 'key', 'image', 'qn_url','created')


class MessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Message
        fields = ('user', 'content', 'pics', 'created')



