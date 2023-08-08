from django.contrib import admin
from .models import Account , Userprofile
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

# Register your models here.
class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()



class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self,object):
        return format_html('<img src="{}" width="30" style="border-radius:50%">'.format(object.profile_picture.url))
    thumbnail.short_decription = 'Profile Picture'
    list_display = ('thumbnail','user', 'city', 'state', 'country')


admin.site.register(Account, AccountAdmin)
admin.site.register(Userprofile,UserProfileAdmin)