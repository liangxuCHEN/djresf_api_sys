from rest_framework import serializers
from media_sys.models import WXuser, Message, QiniuMedia


class WxUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WXuser
        fields = ('id','openid', 'name', 'phone')


class QiniuMediaSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = QiniuMedia
        fields = ('id','name', 'key', 'image', 'qn_url','created')


class MessageSerializer(serializers.HyperlinkedModelSerializer):
    """
    这种序列化会把ｉｄ作为超链接
    """
    class Meta:
        model = Message
        fields = ('id','user', 'content', 'pics', 'created')


class MessageSerializer_json(serializers.ModelSerializer):
    """
    普通的序列化
    """
    class Meta:
        model = Message
        fields = ('id','user', 'content', 'pics', 'created')



class MessageMoreInfoSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'message_id':obj.id,
            'user_id': obj.user_id,
            'user_name': obj.user.name,
            'user_phone': obj.user.phone,
            'content': obj.content,
            'pics': obj.pics,
            'created': obj.created
        }