from django.contrib import admin

# Register your models here.
from media_sys.models import QiniuMedia, WXuser

class QiniuMediaAdmin(admin.ModelAdmin):
    list_display = ('id','key','created')


class WXuserAdmin(admin.ModelAdmin):
    list_display = ('id','name','openid', 'created')


admin.site.register(QiniuMedia, QiniuMediaAdmin)
admin.site.register(WXuser, WXuserAdmin)