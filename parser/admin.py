from django.contrib import admin
from parser.models import *
# Register your models here.

class NicknameInline(admin.StackedInline):
    model = Nickname

@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ('link', 'parseConfigs')
    fields = ['link', 'parseConfigs']
    inlines = [NicknameInline]

@admin.register(Nickname)
class NicknameAdmin(admin.ModelAdmin):
    list_display = ('handler', 'user_id', 'nicknames', 'forumOrigin')
    fields = ['forumOrigin', 'handler', 'user_id', 'nicknames']

@admin.register(BannedFilter)
class BannedFilterAdmin(admin.ModelAdmin):
    list_display = ('purpose', 'filter')
    fields = ['filter', 'purpose']

@admin.register(KeyWordFilter)
class KeyWordFilterAdmin(admin.ModelAdmin):
    list_display = ('purpose', 'filter')
    fields = ['filter', 'purpose']