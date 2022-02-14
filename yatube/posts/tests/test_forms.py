from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post, User, Comment
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
import shutil
import tempfile

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateUpdateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая',
            group=cls.group1,
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Первый',
            post=cls.post,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_user(self):
        """Через форму создается новый пользователь."""
        user_count = User.objects.count()
        form_data = {
            'username': 'Lucifer',
            'password1': 'mandarin300',
            'password2': 'mandarin300',
            'email': 'Lucifer@mail.ru',
            'first_name': 'Владимир',
            'last_name': 'Путин'
        }
        response = self.authorized_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('space_posts:posts'))
        self.assertEqual(User.objects.count(), user_count + 1)
        user_created = User.objects.latest('date_joined')
        self.assertEqual(user_created.username, 'Lucifer')
        self.assertEqual(user_created.email, 'Lucifer@mail.ru')
        self.assertEqual(user_created.first_name, 'Владимир')
        self.assertEqual(user_created.last_name, 'Путин')

    def test_create_post(self):
        """Через форму создается новая запись в БД
         и происодит перенаправление по нужному адресу.
         """
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        post_count = Post.objects.count()
        pk_group = PostCreateUpdateFormTests.group1.pk
        form_data = {
            'text': 'Текст из формы создания',
            'group': pk_group,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('space_posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'space_posts:profile',
            kwargs={'username': PostCreateUpdateFormTests.user.username})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        post_created = Post.objects.latest('pub_date')
        self.assertEqual(post_created.author, PostCreateUpdateFormTests.user)
        self.assertEqual(post_created.text, 'Текст из формы создания')
        self.assertEqual(post_created.group.pk, pk_group)
        self.assertEqual(post_created.image, 'posts/small.gif')

        response = self.authorized_client.get(reverse('space_posts:posts'))
        post_images_list = []
        for resp_context in response.context['page_obj']:
            post_images_list.append(str(resp_context.image))
        self.assertIn('posts/small.gif', post_images_list)

        response = self.authorized_client.get(reverse(
            'space_posts:group_list',
            kwargs={'slug': 'test-slug-1'})
        )
        post_images_list = []
        for resp_context in response.context['page_obj']:
            post_images_list.append(str(resp_context.image))
        self.assertIn('posts/small.gif', post_images_list)
        response = self.authorized_client.get(reverse(
            'space_posts:profile',
            kwargs={'username': 'auth'})
        )
        post_images_list = []
        for resp_context in response.context['page_obj']:
            post_images_list.append(str(resp_context.image))
        self.assertIn('posts/small.gif', post_images_list)

    def test_edit_post(self):
        """Через форму редактируется запись в БД
         и происодит перенаправление по нужному адресу.
         """
        post_count = Post.objects.count()
        # меняем группу для редактированного поста
        pk_old_group = Post.objects.latest('pub_date').group.pk
        old_group_slug = Post.objects.latest('pub_date').group.slug
        if pk_old_group == PostCreateUpdateFormTests.group1.pk:
            pk_new_group = PostCreateUpdateFormTests.group2.pk
        else:
            pk_new_group = PostCreateUpdateFormTests.group1.pk
        pk_post = Post.objects.latest('pub_date').pk
        form_data = {
            'text': 'Текст редактирован',
            'group': pk_new_group,
        }
        response = self.authorized_client.post(
            reverse(
                'space_posts:post_edit',
                kwargs={'post_id': f'{pk_post}'}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'space_posts:post_detail',
            kwargs={'post_id': f'{pk_post}'})
        )
        self.assertEqual(Post.objects.count(), post_count)
        post_edited = Post.objects.latest('pub_date')
        self.assertEqual(post_edited.author, PostCreateUpdateFormTests.user)
        self.assertEqual(post_edited.text, 'Текст редактирован')
        self.assertEqual(post_edited.group.pk, pk_new_group)
        response = self.authorized_client.get(reverse(
            'space_posts:group_list',
            kwargs={'slug': old_group_slug})
        )
        control_list = [x.text for x in response.context['page_obj']]
        self.assertNotIn(post_edited.text, control_list)

    def test_create_post_non_auth_user(self):
        """Неавторизованный юзер не может
        создать новый пост и комментарий.
         """
        post_count = Post.objects.count()
        pk_group = PostCreateUpdateFormTests.group1.pk
        form_data = {
            'text': 'Текст из формы создания',
            'group': pk_group,
        }
        response = self.guest_client.post(
            reverse('space_posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), post_count)

    def test_comment_add_auth_user(self):
        """Авторизованный юзер создает комментарий через форму на странице
        поста. Комментарий появляется на странице поста."""
        comment_count = Comment.objects.count()
        pk_post = Post.objects.latest('pub_date').pk
        new_comment = 'Второй комментарий'
        form_data = {
            'text': new_comment,
        }
        response = self.authorized_client.post(
            reverse('space_posts:add_comment',
                    kwargs={'post_id': f'{pk_post}'}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        list_comment = []
        for comment in response.context['comments']:
            list_comment.append(str(comment))
        self.assertIn(new_comment, list_comment)

    def test_comment_add_non_user(self):
        """Не авторизованный юзер не может создать комментарий, комментарий
        не появляется на странице поста"""
        comment_count = Comment.objects.count()
        pk_post = Post.objects.latest('pub_date').pk
        new_comment = 'Не авторизованный комментарий'
        form_data = {
            'text': new_comment,
        }
        response = self.guest_client.post(
            reverse(
                'space_posts:add_comment',
                kwargs={'post_id': f'{pk_post}'}
            ),
            data=form_data,
            follow=True
        )
        response
        self.assertEqual(Comment.objects.count(), comment_count)
        response = self.guest_client.post(
            reverse(
                'space_posts:post_detail',
                kwargs={'post_id': f'{pk_post}'}
            ),
            data=form_data,
            follow=True
        )
        list_comment = []
        for comment in response.context['comments']:
            list_comment.append(str(comment))
        self.assertNotIn(new_comment, list_comment)

    def test_cashe_index(self):
        """Проверка работы кэша на главной странице - контент не должен
        измениться после удаления поста из БД"""
        response = self.authorized_client.get(reverse('space_posts:posts'))
        cashe_content = response.content
        Post.objects.latest('pub_date').delete()
        response = self.authorized_client.get(reverse('space_posts:posts'))
        self.assertEqual(cashe_content, response.content)
