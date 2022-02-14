from django.test import TestCase, Client
from ..models import Group, Post, User
from http import HTTPStatus


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user1 = User.objects.create_user(username='non_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )
        cls.post1 = Post.objects.create(
            author=cls.user1,
            text='Нередактируемый пост',
        )
        cls.templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{cls.post.pk}/edit/': 'posts/create_post.html',
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
            '/auth/login/': 'users/login.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        cls.except_nonuser_list = [
            '/create/',
            f'/posts/{URLTests.post.pk}/edit/',
            '/auth/password_change/',
            '/auth/password_change/done/'
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_status_code_user(self):
        """Проверка доступности страниц для авторизованного пользователя."""
        for address in URLTests.templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_status_code_non_user(self):
        """Проверка доступности страниц для неавторизованного пользователя."""
        for page in URLTests.templates_url_names:
            if page in URLTests.except_nonuser_list:
                with self.subTest(page=page):
                    response = self.guest_client.get(page)
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
            else:
                with self.subTest(page=page):
                    response = self.guest_client.get(page)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template_edit(self):
        """URL-адрес /posts/post_id/edit/ использует
        соответствующий шаблон для авторизованного пользователя.
        """
        for address, template in URLTests.templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_non_user(self):
        """URL-адрес использует соответствующий шаблон
        для неавторизованного пользователя.
        """
        for address, template in URLTests.templates_url_names.items():
            if address not in URLTests.except_nonuser_list:
                with self.subTest(address=address):
                    response = self.guest_client.get(address)
                    self.assertTemplateUsed(response, template)

    def test_crete_post_redirect_anonymous_on_admin_login(self):
        """Страницы создания и редактирования перенаправят анонимного
        пользователя на страницу логина.
        """
        dict_control = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{URLTests.post.pk}/edit/':
            f'/auth/login/?next=/posts/{URLTests.post.pk}/edit/',
        }
        for address, redirect_page in dict_control.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, redirect_page)

    def test_non_author_edit_post_(self):
        """Аторизованного пользователя - не автора-
        при попытке редактирования перенаправляет
        на страницу просмотра поста.
        """
        response = self.authorized_client.get(
            f'/posts/{URLTests.post1.pk}/edit/',
            follow=True
        )
        redirect_page = f'/posts/{URLTests.post1.pk}/'
        self.assertRedirects(response, redirect_page)

    def test_unexpected_page_check(self):
        """Неизвестная страница дает ошибку 404."""
        response = self.guest_client.get('/unexpected_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
