from django.db import models

# Create your models here.
class WXuser(models.Model):
    """
    微信用户信息
    """
    openid = models.CharField(max_length=64)
    phone = models.CharField(max_length=32)
    name = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.openid

    class Meta:
        ordering = ('created',)


class Message(models.Model):
    """
    用户留言信息，图片信息    
    """
    user = models.ForeignKey(WXuser, on_delete=models.CASCADE,)
    content = models.TextField()
    pics = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)

class QiniuPic(models.Model):
    """
    记录上传到七牛的图片
    """
    key = models.CharField(max_length=512)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)