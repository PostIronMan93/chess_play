from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']

    def clean_username(self):
        username = self.cleaned_data.get("username")

        # Проверка на существование имени пользователя
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_("Пользователь с таким именем уже существует."))

        return username


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
