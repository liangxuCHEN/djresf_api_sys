from django.db import models
from api_sys.settings import QINIU_ACCESS_KEY, QINIU_SECRET_KEY, QINIU_BUCKET_DOMAIN, QINIU_BUCKET_NAME
# Create your models here.
from django.db.models.signals import post_save
from media_sys.tools import Qiqiu, handle_uploaded_file

import uuid
from datetime import datetime
import os


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

class QiniuMedia(models.Model):
    """
    记录上传到七牛的图片
    """
    name = models.CharField(max_length=64)
    key = models.CharField(max_length=512, null=True)
    qn_url = models.URLField(null=True, default='')
    image = models.ImageField(upload_to="qn",blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)

    def save(self, *args, **kwargs):
        file_name = str(uuid.uuid4())[:6]
        self.key = "%s/%s/%s/%s" % (
            self.key,
            datetime.today().strftime("%Y%m%d"),
            file_name,
            self.image
        )
        self.qn_url = "http://%s/%s" % (QINIU_BUCKET_DOMAIN, self.key)
        super(QiniuMedia, self).save(*args, **kwargs)


class QiniuZipModel(models.Model):
    """
    记录上传到七牛的压缩包图片
    """
    name = models.CharField(max_length=64)
    key = models.CharField(max_length=512, null=True)
    image_logs = models.TextField(default="{}")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)


def upload_image(**kwarge):
    # disable the handler during fixture loading
    instance = kwarge['instance']

    # 上传到七牛云服务
    qn = Qiqiu(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
    #key = "%s.%s" % (instance.key, get_file_extension(instance.image.path))
    qn.upload(QINIU_BUCKET_NAME, instance.key, instance.image.path)


def get_file_extension(file_path):
    import imghdr

    extension = imghdr.what(file_path)
    extension = "jpg" if extension == "jpeg" else extension

    return extension

post_save.connect(upload_image, sender=QiniuMedia)