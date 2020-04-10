from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class UserAccountForm(UserCreationForm):
    first_name = forms.CharField(max_length=30,label='First Name', required=True, widget=forms.TextInput(attrs={'class':'input100','placeholder':'First Name'}))
    last_name = forms.CharField(max_length=30, label='Last Name',required=True, widget=forms.TextInput(attrs={'class':'input100','placeholder':'Last Name'}))
    email = forms.EmailField(max_length=50, label='Email',widget=forms.TextInput(attrs={'class':'input100','placeholder':'Email Address'}))
    username=forms.CharField(max_length=50,label='Username',widget=forms.TextInput(attrs={'class':'input100','placeholder':'Username'}))
    password1 = forms.CharField(max_length=32,label='Password',widget=forms.PasswordInput(attrs={'class':'input100','placeholder':'Password'}))
    password2 = forms.CharField(max_length=32, label='Confirm Password',widget=forms.PasswordInput(attrs={'class': 'input100','placeholder':'Confirm Password'}))

    def clean_username(self):
        c_username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=c_username)
        if r.count():
            raise ValidationError("Username already exists")
        return c_username

    def clean_email(self):
        c_email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=c_email)
        if r.count():
            raise ValidationError("Email already exists")
        return c_email

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']

        if password1 and password2 and password1 != password2:
            raise ValidationError("Your Passwords do not match")
        return password2;

    def save(self, commit=True):
        user = User.objects.create_user(self.cleaned_data['username'], first_name=self.cleaned_data['first_name'],
                                        last_name=self.cleaned_data['last_name'],
                                        email=self.cleaned_data['email'],
                                        password=self.cleaned_data['password1']
                                        )
        return user

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, label='Username', widget=forms.TextInput(attrs={'class': 'input100','placeholder':'username'}))
    password1 = forms.CharField(max_length=32, label='Password',widget=forms.PasswordInput(attrs={'class': 'input100','placeholder':'Password'}))