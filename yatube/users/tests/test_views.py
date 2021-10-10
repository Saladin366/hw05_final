from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

User = get_user_model()


class UsersPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='leo')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(UsersPagesTests.user)

    def test_users_pages_uses_correct_template(self):
        """Страницы авторизации использует соответствующий шаблон."""
        pages_templates_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:password_reset'): 'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:reset_token', args=['uidb64', 'token']):
                'users/password_reset_confirm.html',
            reverse('users:reset_done'): 'users/password_reset_complete.html'}
        for page, template in pages_templates_names.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertTemplateUsed(response, template)

    def test_signup_page_show_correct_context(self):
        """Страница регистрации создана с правильным контекстом."""
        response = self.authorized_client.get(reverse('users:signup'))
        form_fields = {'first_name': forms.fields.CharField,
                       'last_name': forms.fields.CharField,
                       'username': forms.fields.CharField,
                       'email': forms.fields.EmailField}
        for field, type_field in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context['form'].fields[field]
                self.assertIsInstance(form_field, type_field)
