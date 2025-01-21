from django import forms
from .models import Books

class BookForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = ['title', 'topic', 'author', 'description', 'image', 'pdf_file', 'content']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'content': forms.Textarea(attrs={'rows': 10, 'placeholder': 'Enter book content here (if not uploading PDF)'}),
        }