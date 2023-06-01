from django.contrib.auth.models import Group
from django.contrib import admin
from .models import User, Follow


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name',)
    list_filter = ('email', 'username',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'user')
    list_filter = ('user',)


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.unregister(Group)
admin.site.site_header = 'Админ-панель сайта Foodgram'
