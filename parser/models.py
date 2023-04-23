from django.db import models

class Forum(models.Model):
    link = models.CharField(max_length=100, unique=True)
    parseConfigs = models.TextField(unique=True, null=True)

    def __str__(self) -> str:
        return self.link

# Telegram @... handlers and their related forum nicknames
class Nickname(models.Model):
    handler = models.CharField(max_length=32, unique=True)
    user_id = models.CharField(max_length=64, unique=True, null=True)
    nicknames = models.TextField(null=True)
    forumOrigin = models.ForeignKey(to = Forum, to_field = 'link', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.handler

class BannedWord(models.Model):
    filter = models.CharField(max_length=50, unique=True, help_text='Word/statement to exclude in search')
    purpose = models.CharField(max_length=50, help_text="For/Для ...")