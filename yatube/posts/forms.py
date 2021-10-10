from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': _('Текст поста'), 'group': _('Группа'),
                  'image': _('Картинка')}
        help_texts = {
            'text': _('Текст нового поста'),
            'group': _('Группа, к которой будет относиться пост')}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
