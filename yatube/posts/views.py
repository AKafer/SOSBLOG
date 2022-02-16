from .models import Post, Group, User, Follow
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required


N_EXEMPLE: int = 10


def index(request):
    post_list = Post.objects.all().select_related('author', 'group')
    paginator = Paginator(post_list, N_EXEMPLE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'index': True
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author', 'group')
    paginator = Paginator(posts, N_EXEMPLE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(
        author=author).select_related('author', 'group')
    number_posts = posts.count()
    paginator = Paginator(posts, N_EXEMPLE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = False
    if str(request.user) != 'AnonymousUser':
        author_list = [x.author for x in request.user.follower.all()]
        following = (author in author_list)
    context = {
        'username': username,
        'number_posts': number_posts,
        'page_obj': page_obj,
        'author': author,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    user_request = request.user
    post = get_object_or_404(Post, id=post_id)
    posts = Post.objects.filter(author=post.author)
    number_posts = posts.count()
    can_edit = user_request == post.author
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'number_posts': number_posts,
        'post_id': post_id,
        'can_edit': can_edit,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        user = request.user
        post = form.save(commit=False)
        post.author = user
        post.save()
        return redirect(f'/profile/{user}/')
    context = {
        'form': form,
        'is_edit': False
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect(f'/posts/{post_id}/')
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    if post.author != request.user:
        return redirect(f'/posts/{post_id}/')
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(f'/posts/{post_id}/')


@login_required
def follow_index(request):
    user = get_object_or_404(User, username=request.user)
    follow_list = user.follower.all().values('author')
    post_list = Post.objects.filter(author__in=follow_list)
    paginator = Paginator(post_list, N_EXEMPLE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'follow': True
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect('/follow/')


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    follow_del = user.follower.get(author=author)
    follow_del.delete()
    return redirect('/follow/')
