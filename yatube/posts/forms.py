from django import forms
from .models import Post, Comment
from django.utils.translation import ugettext_lazy as _
# from django.core.exceptions import ValidationError
# from captcha.fields import CaptchaField


class PostForm(forms.ModelForm):
    # captcha = CaptchaField()
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': _('Текст'),
            'group': _('Группа'),
        }

    # def clean_text(self):
    #     text = self.cleaned_data['text']
    #     if len(text) < 10:
    #         raise ValidationError(
    #           'Такие маленькие посты на этом сайте недопустимы'
    #         )

    #     return text


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': _('Комментарий'),
        }
