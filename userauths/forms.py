from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User, Profile


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Username", "class": "form-control"}),
        max_length=100
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Email", "class": "form-control"})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password", "class": "form-control"})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password", "class": "form-control"})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Enter Username"
        self.fields['email'].label = "Enter Email"
        self.fields['password1'].label = "Enter Password"
        self.fields['password2'].label = "Confirm Password"


class ProfileForm(forms.ModelForm):
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Full Name", "class": "form-control"}),
        max_length=200
    )
    bio = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Bio", "class": "form-control"}),
        required=False  
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Phone", "class": "form-control"}),
        required=False  
    )
    address = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Address", "class": "form-control"}),
        required=False  
    )
    country = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Country", "class": "form-control"}),
        required=False  
    )

    class Meta:
        model = Profile
        fields = ['full_name', 'image', 'bio', 'phone', 'address', 'country']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['full_name'].label = "Full Name"
        self.fields['bio'].label = "Short Bio"
        self.fields['phone'].label = "Phone Number"