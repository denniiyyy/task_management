from django import forms
from django.core.validators import MinLengthValidator, RegexValidator
from .models import CustomUser, Task

class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9_]+$',
                message='Username can only contain letters, numbers, and underscores'
            )
        ]
    )
    email = forms.EmailField()
    password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=8,
        validators=[MinLengthValidator(8, 'Password must be at least 8 characters')]
    )
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            raise forms.ValidationError('Passwords do not match')
        return cleaned_data

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 3:
            raise forms.ValidationError('Title must be at least 3 characters')
        return title

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_picture']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.exclude(id=self.instance.id).filter(email=email).exists():
            raise forms.ValidationError('Email already in use')
        return email