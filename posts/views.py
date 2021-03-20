from django.shortcuts import redirect, render, get_object_or_404
from django.conf import settings
from .models import Post
from .forms import PostForm
from django.views.decorators.http import require_http_methods, require_safe
from django.contrib.auth.decorators import login_required


@require_safe
def home(request):
    posts = Post.objects.all().order_by("-created_at")
    MAPS_API_KEY = settings.MAPS_API_KEY
    context = {
        "posts": posts,
        "MAPS_API_KEY": MAPS_API_KEY,
    }
    return render(request, "posts/home.html", context)


@require_safe
def index(request):

    return render(request, "posts/index.html")


@login_required(login_url="accounts:login", redirect_field_name="")
@require_http_methods(["GET", "POST"])
def create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            # url에서 위도 경도 추출
            url = form.cleaned_data["url"]
            split_url = url.split(",")
            lat = float(split_url[0].split("@")[1])
            lng = float(split_url[1])
            heading = float(split_url[4].replace("h", ""))
            pitch = float(split_url[5].split("t")[0]) - float(90)

            # Post 인스턴스 변수 생성
            post = Post()

            # 데이터 대입
            post.title = form.cleaned_data["title"]
            post.content = form.cleaned_data["content"]
            post.category = form.cleaned_data["category"]
            post.lat = lat
            post.lng = lng
            post.url = url
            post.heading = heading
            post.pitch = pitch
            post.user = request.user
            # Post 인스턴스 저장
            post.save()
            return redirect("posts:home")
    else:
        form = PostForm

    context = {
        "form": form,
    }
    return render(request, "posts/create.html", context)


@require_safe
def detail(request, pk):
    MAPS_API_KEY = settings.MAPS_API_KEY

    post = get_object_or_404(Post, pk=pk)
    context = {
        "MAPS_API_KEY": MAPS_API_KEY,
        "post": post,
    }
    return render(request, "posts/detail.html", context)


@login_required(login_url="accounts:login", redirect_field_name="")
@require_http_methods(["GET", "POST"])
def update(request, pk):
    post = Post.objects.get(pk=pk)
    if post.user != request.user:
        return redirect("posts:detail", post.id)
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            # url에서 위도 경도 추출
            url = form.cleaned_data["url"]
            split_url = url.split(",")
            lat = split_url[0].split("@")[1]
            lng = split_url[1]

            post.title = form.cleaned_data["title"]
            post.content = form.cleaned_data["content"]
            post.category = form.cleaned_data["category"]
            post.lat = lat
            post.lng = lng
            post.url = url
            post.save()
            return redirect("posts:detail", post.id)

    else:
        form = PostForm(
            initial={
                "title": post.title,
                "content": post.content,
                "category": post.category,
                "url": post.url,
            }
        )

    context = {
        "form": form,
        "post": post,
    }
    return render(request, "posts/update.html", context)


@login_required(login_url="accounts:login", redirect_field_name="")
@require_http_methods(["POST"])
def delete(request, pk):
    post = Post.objects.get(pk=pk)
    if post.user != request.user:
        return redirect("posts:detail", post.id)

    if request.method == "POST":
        post.delete()
        return redirect("posts:home")

    return redirect("posts:detail", post.id)
