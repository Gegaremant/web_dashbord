from django import forms
from .models import Portal


class PortalForm(forms.ModelForm):
    """Форма для создания и редактирования порталов"""
    
    class Meta:
        model = Portal
        fields = ['title', 'url', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Название портала',
                'required': True
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://example.com',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Описание (необязательно)',
                'rows': 3
            }),
        }
        labels = {
            'title': 'Название',
            'url': 'URL адрес',
            'description': 'Описание'
        }
