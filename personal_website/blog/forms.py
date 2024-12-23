"""Формы блога."""

from django import forms
from tinymce.widgets import TinyMCE

from blog.models import Comment


class NewCommentForm(forms.ModelForm):
    """Форма создания нового комментария к статье."""

    content = forms.CharField(
        label="",
        widget=TinyMCE(
            attrs={
                "class": "form-control",
                "placeholder": "Оставить комментарий",
                "rows": 4,
            },
        ),
    )

    class Meta:  # noqa: D106
        model = Comment
        fields = ("content",)

    def __init__(self, *args, **kwargs) -> None:
        """Убрать название поля для тела комментария."""
        super().__init__(*args, **kwargs)
        self.fields["content"].label = ""
