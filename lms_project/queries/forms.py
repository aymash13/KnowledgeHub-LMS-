from django import forms
from .models import Query

class QueryForm(forms.ModelForm):
    class Meta:
        model = Query
        fields = ['title', 'description', 'course', 'lesson']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your query title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe your issue'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'lesson': forms.Select(attrs={'class': 'form-select'}),
        }