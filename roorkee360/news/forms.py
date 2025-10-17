# news/forms.py - Create this NEW file
from django import forms
from .models import Comment
import re

class CommentForm(forms.ModelForm):
    """Form for submitting comments"""
    
    class Meta:
        model = Comment
        fields = ['name', 'email', 'content']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': True,
                'maxlength': 100
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
                'required': True
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your thoughts...',
                'rows': 4,
                'required': True,
                'maxlength': 1000
            })
        }
        labels = {
            'name': 'Name *',
            'email': 'Email *',
            'content': 'Comment *'
        }
    
    def clean_name(self):
        """Validate name field"""
        name = self.cleaned_data.get('name')
        if not name or len(name.strip()) < 2:
            raise forms.ValidationError("Name must be at least 2 characters long.")
        
        # Check for invalid characters
        if not re.match(r'^[a-zA-Z\s.]+$', name):
            raise forms.ValidationError("Name can only contain letters and spaces.")
        
        return name.strip()
    
    def clean_email(self):
        """Validate email field"""
        email = self.cleaned_data.get('email')
        
        # Basic email validation (Django already does this, but we can add custom rules)
        if email and len(email) > 254:
            raise forms.ValidationError("Email address is too long.")
        
        return email.lower().strip()
    
    def clean_content(self):
        """Validate comment content"""
        content = self.cleaned_data.get('content')
        
        if not content or len(content.strip()) < 10:
            raise forms.ValidationError("Comment must be at least 10 characters long.")
        
        # Check for spam keywords (basic spam detection)
        spam_keywords = ['viagra', 'casino', 'lottery', 'click here', 'buy now']
        content_lower = content.lower()
        
        for keyword in spam_keywords:
            if keyword in content_lower:
                raise forms.ValidationError("Your comment contains prohibited content.")
        
        # Check for too many links (spam prevention)
        link_count = content.count('http://') + content.count('https://')
        if link_count > 2:
            raise forms.ValidationError("Comments cannot contain more than 2 links.")
        
        return content.strip()