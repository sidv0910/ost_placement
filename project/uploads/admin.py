import os
from django.conf import settings
from django.contrib import admin
from .models import Profile

class ProfileAdminInfo(admin.ModelAdmin):
    model = Profile
    list_display = ('email', 'contact', 'cv')

    def delete_model(self, request, obj):
        os.remove(os.path.join(settings.MEDIA_ROOT, 'cv/{0}.pdf'.format(obj.email)))
        obj.delete()

    def delete_queryset(self, request, queryset):
        for i in queryset:
            os.remove(os.path.join(settings.MEDIA_ROOT, 'cv/{0}.pdf'.format(i.email)))
            i.delete()

admin.site.register(Profile, ProfileAdminInfo)