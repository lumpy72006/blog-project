from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "featured_image", "status", "pub_date"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "pub_date": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
        }
        # Content field will be rendered manually in HTML using Trix


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100, required=True)
