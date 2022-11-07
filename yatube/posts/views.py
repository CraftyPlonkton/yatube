from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User

POSTS_ON_PAGE = 10


@cache_page(20)
def index(request):
    template = "posts/index.html"
    posts = Post.objects.all()
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj}
    return render(request, template, context)


def group_posts(request, slug):
    template = "posts/group_list.html"
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"group": group, "page_obj": page_obj}
    return render(request, template, context)


def profile(request, username):
    template = "posts/profile.html"
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=author).exists()
    )
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"author": author, "page_obj": page_obj, "following": following}
    return render(request, template, context)


def post_detail(request, post_id):
    template = "posts/post_detail.html"
    form = CommentForm()
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post=post)
    count = Post.objects.filter(author=post.author).count()
    is_owner = False
    if request.user == post.author:
        is_owner = True
    context = {
        "post": post,
        "comments": comments,
        "count": count,
        "is_owner": is_owner,
        "form": form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = "posts/create_post.html"
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, template, {"form": form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("posts:profile", request.user.username)


@login_required
def post_edit(request, post_id):
    template = "posts/create_post.html"
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect("posts:post_detail", post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if not form.is_valid():
        return render(
            request,
            template,
            {"form": form, "post_id": post_id, "is_edit": True}
        )
    edited_post = form.save(commit=False)
    edited_post.author = request.user
    edited_post.save()
    return redirect("posts:post_detail", post_id)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = Post.objects.get(pk=post_id)
        comment.save()
    return redirect("posts:post_detail", post_id)


@login_required
def follow_index(request):
    template = "posts/follow.html"
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj}
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    if (
        request.user.username == username
        or Follow.objects.filter(
            user=request.user,
            author=get_object_or_404(User, username=username)
        ).exists()
    ):
        return redirect("posts:profile", username)
    Follow.objects.create(
        user=request.user, author=get_object_or_404(User, username=username)
    )
    return redirect("posts:profile", username)


@login_required
def profile_unfollow(request, username):
    following = get_object_or_404(
        Follow,
        user=request.user,
        author=get_object_or_404(User, username=username)
    )
    following.delete()
    return redirect("posts:profile", username)
