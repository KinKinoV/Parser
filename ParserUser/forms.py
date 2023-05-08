from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, AuthenticationForm


class RegisterUserForm(UserCreationForm):
    
    def init(self,*args,**kwargs):
        super(RegisterUserForm,self).__init__(*args,**kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control text-center',
            'placeholder': 'Enter your password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password',
        })
    
    
    username=forms.CharField(max_length=40, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username', }))
    password1=forms.CharField(max_length=40, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}))
    password2=forms.CharField(max_length=40, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}))
    
    class Meta:
        model = User
        fields = ('username','password1','password2',)
    
    def checking_usernames(self):
        username=self.cleaned_data.get('username')
        user_qs=User.objects.filter(username=username)
        if user_qs.exists():
            raise forms.ValidationError('Username already used')
        return username
    

class LoginUserForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your username',
        })
        
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password',
        })
    class Meta:
        fields = ['username', 'password']


        
class EditSettingsForm(UserChangeForm):
    is_active=forms.CharField(max_length=100,widget=forms.CheckboxInput(attrs={'class':'form-check'}))
    last_login=forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class':'form-control'}))
    date_joined=forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class':'form-control'}))

    
    class Meta:
        model = User
        fields = ('username','password','last_login','date_joined','is_active')

class PasswordChangingForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','type':'password'}))
    new_password1 = forms.CharField(max_length=40,widget=forms.PasswordInput(attrs={'class':'form-control','type':'password'}))
    new_password2 = forms.CharField(max_length=40,widget=forms.PasswordInput(attrs={'class':'form-control','type':'password'}))
    #address=forms.CharField(max_length=100)
    

    
    class Meta:
        model = User
        fields = ('old_password', 'new_password1','new_password2')