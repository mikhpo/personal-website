"""Тесты форм блога."""

from django.test import TestCase

from blog.forms import NewCommentForm
from personal_website.utils import generate_random_text


class CommentFormTest(TestCase):
    """Проверка корректности TestCase формы создания комментария."""

    def test_comment_form_fields(self) -> None:
        """Проверка набора полей в форме комментария и предзаполненых значений."""
        form = NewCommentForm()
        fields = form.fields
        self.assertIn("content", fields)
        self.assertEqual(fields["content"].initial, None)

    def test_comment_form_has_no_labels(self) -> None:
        """Проверяет, что у полей формы создания комментария нет названий."""
        form = NewCommentForm()
        self.assertEqual(form.fields["content"].label, "")

    def test_comment_author_detected(self) -> None:
        """Проверяет, что комментарий не может быть пустым."""
        form = NewCommentForm(data={"content": ""})
        self.assertFalse(form.is_valid())
        form = NewCommentForm(data={"content": generate_random_text(10)})
        self.assertTrue(form.is_valid())
