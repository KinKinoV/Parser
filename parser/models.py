from django.db import models

class Forum(models.Model):
    link = models.CharField(max_length=100, unique=True)
    parseConfigs = models.TextField(unique=True, null=True)

    def __str__(self) -> str:
        return self.link

# Telegram @... handlers
class TgHandler(models.Model):
    handler = models.CharField(max_length=32, unique=True)
    forumOrigin = models.ForeignKey(to = Forum, to_field = 'link', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.handler

class ForumNickname(models.Model):
    nickname = models.CharField(max_length=50)
    tgHandlers = models.ManyToManyField(to = TgHandler, blank=True, related_name='nicknames')
    forumOrigin = models.ForeignKey(to = Forum, to_field='link', on_delete= models.CASCADE)

    def __str__(self) -> str:
        return self.nickname

class BannedWord(models.Model):
    filter = models.CharField(max_length=50, unique=True, help_text='Word/statement to exclude in search')
    purpose = models.CharField(max_length=50, help_text="For/Для ...")