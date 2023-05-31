from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from messaging.forms import CustomUserCreationForm
from messaging.models import GroupMessage, MessagingGroup


@login_required
def home(request):
    return render(request, "home.html",
                  {"num_unread_chats": MessagingGroup.objects
                  .filter(members=request.user)
                  .exclude(read_list=request.user)
                  .count()})


@login_required
def profile(request):
    return render(request, "registration/profile.html")


def create_account(request):
    if request.method == "GET":
        return render(request, "registration/create_account.html", {"form": CustomUserCreationForm()})
    elif request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        form.save()
        return redirect("login")
