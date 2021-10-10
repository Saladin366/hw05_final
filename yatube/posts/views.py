from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'group': group, 'page_obj': page_obj}
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'author': author}
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author).exists()
        context['following'] = following
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    comments = post.comments.all()
    form = CommentForm()
    context = {'post': post, 'author': author, 'comments': comments,
               'form': form}
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    groups = Group.objects.all()
    if request.method != 'POST':
        form = PostForm()
        return render(request, template, {'form': form, 'groups': groups})
    form = PostForm(request.POST, files=request.FILES)
    if not form.is_valid():
        return render(request, template, {'form': form, 'groups': groups})
    username = request.user.username
    author = get_object_or_404(User, username=username)
    post = form.save(commit=False)
    post.author = author
    post.save()
    return redirect('posts:profile', username=username)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    groups = Group.objects.all()
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    if request.method != 'POST':
        form = PostForm()
        return render(request, template, {'form': form, 'groups': groups,
                                          'post': post})
    form = PostForm(request.POST, files=request.FILES, instance=post)
    if not form.is_valid():
        return render(request, template, {'form': form, 'groups': groups,
                                          'post': post})
    form.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    posts_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts_list, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow, user=request.user, author=author)
    follow.delete()
    return redirect('posts:profile', username=username)
