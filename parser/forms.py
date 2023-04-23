from django import forms
from django.forms import ModelForm
from .models import Nickname


class userSearchFromModel(ModelForm):
    class Meta:
        model = Nickname
        fields= ('handler','forumOrigin')
        labels = {
            'handler': 'input nickname',
            'forumOrigin':'Select forum name'
        }
        widgets = {
            'handler':forms.TextInput(attrs={'class':'form-control','placeholder':'Input nickname'}),
            'forumOrigin': forms.Select(attrs={'class':'form-control','placeholder':'Input nickname'}),
        }