from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post, User
from ..views import N_EXEMPLE


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # число постов
        cls.N_POSTS_ALL: int = 12
        # Создаем двух юзеров и две группы
        cls.user1 = User.objects.create_user(username='Толстой')
        cls.user2 = User.objects.create_user(username='Пушкин')
        cls.group1 = Group.objects.create(
            title='Группа-1',
            slug='test-slug-1',
            description='Описание Группы-1',
        )
        cls.group2 = Group.objects.create(
            title='Группа-2',
            slug='test-slug-2',
            description='Описание Группы-2',
        )
        # контрольный список
        cls.control_list = [(
            'Толстой' if i < 7 else 'Пушкин',
            f'Текст поста {i}',
            'Группа-2' if i % 2 == 0 else 'Группа-1')
            for i in range(1, cls.N_POSTS_ALL + 1, 1)
        ]
        # 12 новых объектов
        objs = [
            Post(
                author=cls.user1 if i < 7 else cls.user2,
                text=f'Текст поста {i}',
                group=cls.group2 if i % 2 == 0 else cls.group1,
            )
            for i in range(1, cls.N_POSTS_ALL + 1, 1)
        ]
        Post.objects.bulk_create(objs=objs)
        cls.N_POSTS_GROUPLIST = Post.objects.filter(group=cls.group1).count()
        cls.N_POSTS_PROFILE = Post.objects.filter(author=cls.user1).count()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post_id = Post.objects.earliest('pub_date').id
        templates_pages_names = {
            reverse('space_posts:posts'): 'posts/index.html',
            reverse('space_posts:group_list', kwargs={'slug': 'test-slug-1'}):
                'posts/group_list.html',
            reverse('space_posts:profile', kwargs={'username': 'Толстой'}):
                'posts/profile.html',
            reverse(
                'space_posts:post_detail',
                kwargs={'post_id': f'{post_id}'}
            ):
                'posts/post_detail.html',
            reverse('space_posts:post_create'):
                'posts/create_post.html',
            reverse('space_posts:post_edit', kwargs={'post_id': f'{post_id}'}):
                'posts/create_post.html',
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
            reverse('users:signup'): 'users/signup.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_first_page_contains_ten_records(self):
        """Проверка пагинатора на первой странице страницы index"""
        response = self.authorized_client.get(reverse('space_posts:posts'))
        self.assertEqual(
            len(response.context['page_obj']),
            N_EXEMPLE
        )

    def test_home_second_page_contains_three_records(self):
        """Проверка пагинатора на второй странице страницы index"""
        N_POSTS_HOME_SECOND = PostPagesTests.N_POSTS_ALL - N_EXEMPLE
        response = self.authorized_client.get(reverse(
            'space_posts:posts') + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            N_POSTS_HOME_SECOND
        )

    def test_group_list_first_page_contains_six_records(self):
        """Проверка пагинатора на первой странице страницы group_list"""
        response = self.authorized_client.get(reverse(
            'space_posts:group_list',
            kwargs={'slug': 'test-slug-1'})
        )
        self.assertEqual(
            len(response.context['page_obj']),
            PostPagesTests.N_POSTS_GROUPLIST
        )

    def test_profile_first_page_contains_six_records(self):
        """Проверка пагинатора на первой странице страницы profile"""
        response = self.authorized_client.get(reverse(
            'space_posts:profile',
            kwargs={'username': 'Толстой'})
        )
        self.assertEqual(
            len(response.context['page_obj']),
            PostPagesTests.N_POSTS_PROFILE
        )

    def test_home_pages_show_correct_context(self):
        """Шаблон index.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('space_posts:posts'))
        n_post: int = 0
        for resp_context in response.context['page_obj']:
            post = (
                str(resp_context.author),
                resp_context.text,
                str(resp_context.group),
            )
            self.assertIn(post, PostPagesTests.control_list)
            n_post += 1

        response = self.authorized_client.get(reverse(
            'space_posts:posts') + '?page=2'
        )
        for resp_context in response.context['page_obj']:
            post = (
                str(resp_context.author),
                resp_context.text,
                str(resp_context.group),
            )
            self.assertIn(post, PostPagesTests.control_list)
            n_post += 1
        self.assertEqual(n_post, len(PostPagesTests.control_list))

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'space_posts:group_list',
            kwargs={'slug': 'test-slug-1'})
        )
        control_list = [
            x for x in PostPagesTests.control_list if x[2] == 'Группа-1'
        ]
        n_post: int = 0
        for resp_context in response.context['page_obj']:
            post = (
                str(resp_context.author),
                resp_context.text,
                str(resp_context.group),
            )
            self.assertIn(post, control_list)
            n_post += 1
        self.assertEqual(n_post, len(control_list))

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        control_name = 'Пушкин'
        response = self.authorized_client.get(reverse(
            'space_posts:profile',
            kwargs={'username': control_name})
        )
        control_list = [
            x for x in PostPagesTests.control_list if x[0] == control_name
        ]
        n_post: int = 0
        for resp_context in response.context['page_obj']:
            post = (
                str(resp_context.author),
                resp_context.text,
                str(resp_context.group),
            )
            self.assertIn(post, control_list)
            n_post += 1
        self.assertEqual(n_post, len(control_list))

    def test_follow_index_show_correct_context(self):
        """Шаблон follow сформирован с правильным контекстом."""
        author = PostPagesTests.user2
        response = self.authorized_client.get(
            reverse('space_posts:profile_follow',
                    kwargs={'username': author})
        )
        response = self.authorized_client.get(
            reverse('space_posts:follow_index')
        )
        control_list = [
            x for x in PostPagesTests.control_list if x[0]
            == author.username
        ]
        n_post: int = 0
        for resp_context in response.context['page_obj']:
            post = (
                str(resp_context.author),
                resp_context.text,
                str(resp_context.group),
            )
            self.assertIn(post, control_list)
            n_post += 1
        self.assertEqual(n_post, len(control_list))
