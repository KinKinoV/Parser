from django.contrib import admin
from parser.models import *
# Register your models here.

class TgHandlerInline(admin.StackedInline):
    model = TgHandler

class ForumNicknameInline(admin.StackedInline):
    model = ForumNickname

@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ('link', 'parseConfigs')
    fields = ['link', 'parseConfigs']
    inlines = [TgHandlerInline, ForumNicknameInline]


class TgHandlerNicknamesInline(admin.StackedInline):
    model = ForumNickname.tgHandlers.through

@admin.register(TgHandler)
class TgHandlerAdmin(admin.ModelAdmin):
    list_display = ('handler', 'forumOrigin')
    fields = ['forumOrigin', 'handler']

    inlines = [TgHandlerNicknamesInline]

@admin.register(ForumNickname)
class ForumNicknameAdmin(admin.ModelAdmin):
    pass

@admin.register(BannedWord)
class BannedWordAdmin(admin.ModelAdmin):
    list_display = ('filter', 'purpose')
    fields = ['filter', 'purpose']