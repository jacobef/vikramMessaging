from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from messaging.forms import CustomUserCreationForm
from messaging.models import GroupMessage, MessagingGroup, CustomUser, DirectMessageLine


@login_required
def home(request):
    return render(request, "home.html",
                  {"num_unread_chats": MessagingGroup.objects
                  .filter(members=request.user)
                  .exclude(read_list=request.user)
                  .count(),
                   "num_unread_mentions": MessagingGroup.objects
                  .filter(members=request.user)
                  .filter(mentioned_users=request.user)
                  .count(),
                   "num_unread_dms": DirectMessageLine.objects
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
        form = CustomUserCreationForm(request.POST, request.FILES)
        form.save()
        return redirect("login")


class EditProfile(UpdateView):
    model = CustomUser
    template_name = "registration/edit_profile.html"
    fields = ("first_name", "last_name", "email", "profile_pic")
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user
