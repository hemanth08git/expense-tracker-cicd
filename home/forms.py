from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class SignupForm(UserCreationForm):
    fname = forms.CharField(max_length=30, required=True, label="First Name")
    lname = forms.CharField(max_length=30, required=True, label="Last Name")
    email = forms.EmailField(required=True)
    profession = forms.ChoiceField(
        choices=[
            ('Employee', 'Employee'),
            ('Business', 'Business'),
            ('Student', 'Student'),
            ('Other', 'Other')
        ],
        required=True
    )
    Savings = forms.DecimalField(required=True, min_value=0, decimal_places=2)
    income = forms.DecimalField(required=True, min_value=0, decimal_places=2)

    class Meta:
        model = User
        fields = ['username', 'fname', 'lname', 'email',
                  'profession', 'Savings', 'income',
                  'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove autohelp text if it's causing issues
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['fname']
        user.last_name = self.cleaned_data['lname']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Create or update UserProfile
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'profession': self.cleaned_data['profession'],
                    'Savings': self.cleaned_data['Savings'],
                    'income': self.cleaned_data['income']
                }
            )
        return user

    def clean_username(self):
        uname = self.cleaned_data.get("username")
        if not uname:
            raise forms.ValidationError("Username is required.")
        if len(uname) > 15:
            raise forms.ValidationError("Username must be max 15 characters.")
        if not uname.isalnum():
            raise forms.ValidationError("Username should be alphanumeric.")
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError("Username already exists.")
        return uname

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError("Email is required.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")
        return email