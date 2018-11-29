from django.contrib import admin

# Register your models here.
from media_sys.models import QiniuPic, WXuser

class QiniuPicAdmin(admin.ModelAdmin):
    list_display = ('id','key','created')


class WXuserAdmin(admin.ModelAdmin):
    list_display = ('id','name','openid', 'created')


admin.site.register(QiniuPic, QiniuPicAdmin)
admin.site.register(WXuser, WXuserAdmin)