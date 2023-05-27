from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView

from messaging.models import MessagingGroup, GroupMessage, DirectMessage


@login_required
def view_chats(request):
    return render(request, "group_chats.html",
                  {"chats": MessagingGroup.objects.filter(members=request.user.pk)})


@login_required
def view_chat(request, chat_pk):
    group = MessagingGroup.objects.get(pk=chat_pk)
    if request.method == "GET":
        if request.user in group.members.all():
            return render(request, "group_chat.html",
                          {"chat": MessagingGroup.objects.get(pk=chat_pk),
                           "messages": GroupMessage.objects.filter(to__pk=chat_pk)})
        else:
            return render(request, "not_in_group.html")
    elif request.method == "POST":
        new_message = GroupMessage(content=request.POST["message"],
                                   by=request.user,
                                   to=group,
                                   time_sent=timezone.now())
        new_message.save()
        return redirect("messaging:view_chat", chat_pk=chat_pk)


@login_required
def invite(request, chat_pk):
    group = MessagingGroup.objects.get(pk=chat_pk)

    if request.method == "GET":
        return render(request, "invite.html",
                      {"uninvited_users": User.objects.exclude(messaging_group=group),
                       "chat": group})
    elif request.method == "POST":
        if request.user not in group.members.all():
            return HttpResponse("You can't invite people to a group you're not in")
        for user_pk in request.POST.getlist("users"):
            group.members.add(int(user_pk))
        return redirect("messaging:view_chat", chat_pk=chat_pk)


@method_decorator(login_required, name="dispatch")
class NewChat(CreateView):
    model = MessagingGroup
    fields = ["name"]
    template_name = "new_chat.html"
    success_url = reverse_lazy("messaging:view_chats")

    def form_valid(self, form):
        form.instance.save()
        form.instance.members.add(self.request.user.pk)
        form.instance.save()
        return super().form_valid(form)


def leave_chat(request, chat_pk):
    chat = MessagingGroup.objects.get(pk=chat_pk)
    chat.members.remove(request.user.pk)
    return redirect("messaging:view_chats")


def view_dms(request):
    return render(request, "view_dms.html", {"users": User.objects.all()})


def view_dm(request, user_pk):
    other_user = User.objects.get(pk=user_pk)
    if request.method == "GET":
        return render(request, "view_dm.html",
                      {"messages":
                           DirectMessage.objects.filter(by=request.user, to=other_user)
                      .union(DirectMessage.objects.filter(by=other_user, to=request.user))})
    elif request.method == "POST":
        message = DirectMessage(by=request.user, to=other_user, time_sent=timezone.now(),
                                content=request.POST["message"])
        message.save()
        return redirect("messaging:view_dm", user_pk=user_pk)