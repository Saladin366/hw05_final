from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание тестовой группы')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст тестового поста')

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group),
                         'Проверьте правильность object_name у модели Group')
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post),
                         'Проверьте правильность object_name у модели Post')

    def test_verbose_name(self):
        """Проверяем, что у модели Post verbose_name совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {'text': 'Текст поста',
                          'pub_date': 'Дата публикации',
                          'author': 'Автор',
                          'group': 'Группа'}
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(post._meta.get_field(field).verbose_name,
                                 expected_value,
                                 f'Проверьте verbose_name поля {field}')

    def test_help_text(self):
        """Проверяем, что у модели Post help_text совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_text = {'text': 'Введите текст поста',
                           'group': 'Выберите группу'}
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(post._meta.get_field(field).help_text,
                                 expected_value,
                                 f'Проверьте help_text поля {field}')
