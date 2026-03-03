from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile


# 🔹 Signup Form
class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# 🔹 Login Form
class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


# 🔹 Profile Update Form
class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, label='First Name')
    last_name = forms.CharField(max_length=150, required=False, label='Last Name')
    email = forms.EmailField(required=True)

    class Meta:
        model = Profile
        fields = ['bio', 'interests', 'profile_picture', 'reading_goal']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'interests': forms.TextInput(attrs={'placeholder': 'Enter interests separated by commas...'}),
            'reading_goal': forms.NumberInput(attrs={'placeholder': 'Books you want to read this year'}),
        }

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user_instance:
            self.fields['first_name'].initial = self.user_instance.first_name
            self.fields['last_name'].initial = self.user_instance.last_name
            self.fields['email'].initial = self.user_instance.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user_instance:
            self.user_instance.first_name = self.cleaned_data.get('first_name', '')
            self.user_instance.last_name = self.cleaned_data.get('last_name', '')
            self.user_instance.email = self.cleaned_data.get('email', '')
            if commit:
                self.user_instance.save()
                profile.save()
        return profile
