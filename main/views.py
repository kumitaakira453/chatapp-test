from django.contrib import auth
from django.contrib.auth import views as auth_views
from .forms import (
    LoginForm,
    SignUpForm,
    TalkForm,
    UsernameChangeForm,
    EmailChangeForm,
)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Talk, User
from django.urls import reverse_lazy


def index(request):
    print(request.user)

    return render(request, "main/index.html")


def signup(request):
    if request.method == "GET":
        form = SignUpForm()
    elif request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            # モデルに情報を追加する
            form.save()
            # 入力されたデータをformから取得
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            # usernameとpasswordを引数として存在すればuser.backend（認証バックエンド属性）を持つUserを,なければnoneを返す
            user = auth.authenticate(username=username, password=password)
            # ユーザーであることが確認されるとログインできる
            if user:
                # signupと同時にloginを行う
                auth.login(request, user)

            return redirect("index")

    context = {"form": form}
    return render(request, "main/signup.html", context)


class LoginView(auth_views.LoginView):
    authentication_form = LoginForm
    template_name = "main/login.html"


# デコレーター
@login_required
def friends(request):
    friends = User.objects.exclude(id=request.user.id)
    sorted_friends = []
    for friend in friends:
        talks = Talk.objects.filter(
            Q(sender=friend, receiver=request.user)
            | Q(sender=request.user, receiver=friend)
        ).order_by("-time")
        # データとしてまとめて持っておくもので可変でない方が良い
        if talks:
            sorted_friends.append((friend, True, talks[0].time))
        else:
            sorted_friends.append((friend, False, None))
        sorted_friends.sort(key=lambda x: (x[1], x[2]), reverse=True)
    context = {"friends": sorted_friends}
    return render(request, "main/friends.html", context)


@login_required
def settings(request):
    return render(request, "main/settings.html")


@login_required
def talk_room(request, user_id):
    friend = get_object_or_404(User, id=user_id)
    talks = Talk.objects.filter(
        Q(sender=request.user, receiver=friend)
        | Q(sender=friend, receiver=request.user)
    ).order_by("time")

    if request.method == "GET":
        form = TalkForm()
    elif request.method == "POST":
        form = TalkForm(request.POST)
        if form.is_valid():
            new_talk = form.save(commit=False)
            new_talk.sender = request.user
            new_talk.receiver = friend
            new_talk.save()
            return redirect("talk_room", friend.id)
    context = {
        "form": form,
        "friend": friend,
        "talks": talks,
    }
    return render(request, "main/talk_room.html", context)


@login_required
def username_change(request):
    if request.method == "GET":
        form = UsernameChangeForm(instance=request.user)
    elif request.method == "POST":
        form = UsernameChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("username_change_done")
    context = {
        "form": form,
    }
    return render(request, "main/username_change.html", context)


@login_required
def username_change_done(request):
    return render(request, "main/username_change_done.html")


@login_required
def email_change(request):
    if request.method == "GET":
        form = EmailChangeForm(instance=request.user)
    elif request.method == "POST":
        form = EmailChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("email_change_done")

    context = {"form": form}
    return render(request, "main/email_change.html", context)


@login_required
def email_change_done(request):
    return render(request, "main/email_change_done.html")


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = "main/password_change.html"
    success_url = reverse_lazy("password_change_done")


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = "main/password_change_done.html"


class LogoutView(auth_views.LogoutView):
    pass
