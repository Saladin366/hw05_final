from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostsFormsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_users_form_create_user(self):
        """Валидная форма создает нового пользователя."""
        user_count = User.objects.count()
        form_data = {'username': 'leo', 'password1': 'userpassword',
                     'password2': 'userpassword'}
        response = self.guest_client.post(reverse('users:signup'),
                                          data=form_data, follow=True)
        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertTrue(User.objects.filter(username='leo').exists())
        self.assertRedirects(response, reverse('posts:index'))
