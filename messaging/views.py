import rsa
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView
from django.db.models import Q

from messaging.models import MessagingGroup, GroupMessage, DirectMessage, DirectMessageLine, CustomUser


@login_required
def view_chats(request):
    return render(request, "group_chats.html",
                  {"chats": MessagingGroup.objects.filter(members=request.user.pk)})


@login_required
def view_chat(request, chat_pk):
    group = MessagingGroup.objects.get(pk=chat_pk)
    if request.method == "GET":
        if request.user in group.members.all():
            group.read_list.add(request.user)
            group.save()
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
        group.read_list.clear()
        group.read_list.add(request.user)
        group.save()
        return redirect("messaging:view_chat", chat_pk=chat_pk)


@login_required
def invite(request, chat_pk):
    group = MessagingGroup.objects.get(pk=chat_pk)

    if request.method == "GET":
        return render(request, "invite.html",
                      {"uninvited_users": CustomUser.objects.exclude(messaging_groups=group).exclude(banned_from=group).all(),
                       "chat": group})
    elif request.method == "POST":
        if request.user not in group.members.all():
            return HttpResponse("You can't invite people to a group you're not in")
        for user_pk in request.POST.getlist("users"):
            user = CustomUser.objects.get(pk=user_pk)
            if user not in group.ban_list.all():
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
        form.instance.read_list.add(self.request.user.pk)
        form.instance.save()
        return super().form_valid(form)


@login_required
def leave_chat(request, chat_pk):
    chat = MessagingGroup.objects.get(pk=chat_pk)
    chat.members.remove(request.user.pk)
    return redirect("messaging:view_chats")


@login_required
def view_dms(request):
    return render(request, "view_dms.html",
                  {"dm_lines": DirectMessageLine.objects.filter(members=request.user)})


@login_required
def view_dm_line(request, dm_line_pk):
    assert isinstance(request.user, CustomUser)

    dm_line = DirectMessageLine.objects.get(pk=dm_line_pk)
    other_user = dm_line.members.exclude(pk=request.user.pk).get()
    if request.method == "GET":
        dm_line.read_list.add(request.user)
        dm_line.save()
        return render(request, "view_dm_line.html",
                      {"messages": dm_line.messages.all(),
                       "other_user": other_user,
                       "private_key": rsa.PrivateKey.load_pkcs1(request.user.private_key)})
    elif request.method == "POST":
        dm_line.read_list.clear()
        dm_line.read_list.add(request.user)
        dm_line.save()

        message_content: str = request.POST["message"]
        encrypted_message = rsa.encrypt(message_content.encode("utf8"), rsa.PublicKey.load_pkcs1(other_user.public_key))
        message = DirectMessage(by=request.user, to=dm_line, time_sent=timezone.now(),
                                content=encrypted_message)
        message.save()
        return redirect("messaging:view_dm_line", dm_line_pk=dm_line_pk)


@login_required
def new_dm_line(request):
    if request.method == "GET":
        return render(request, "new_dm_line.html", {"users": CustomUser.objects.exclude(pk=request.user.pk).all()})
    elif request.method == "POST":
        other_user = CustomUser.objects.get(pk=int(request.POST["other_user"]))
        existing_line = DirectMessageLine.objects.filter(members=request.user).filter(members=other_user)
        if existing_line.exists():
            return redirect("messaging:view_dm_line", dm_line_pk=existing_line.get().pk)
        dm_line = DirectMessageLine()
        dm_line.save()
        dm_line.members.add(request.user)
        dm_line.members.add(other_user)
        dm_line.read_list.add(request.user)
        dm_line.read_list.add(other_user)
        dm_line.save()
        return redirect("messaging:view_dm_line", dm_line_pk=dm_line.pk)


@login_required
def delete_dm(request, dm_pk):
    dm = DirectMessage.objects.get(pk=dm_pk)
    if dm.by == request.user:
        dm.delete()
    return redirect("messaging:view_dm_line", dm_line_pk=dm.to.pk)


@login_required
def delete_gm(request, gm_pk):
    gm = GroupMessage.objects.get(pk=gm_pk)
    if gm.by == request.user:
        gm.delete()
    return redirect("messaging:view_chat", chat_pk=gm.to.pk)


def delete_dm_line(request, dm_line_pk):
    dm_line = DirectMessageLine.objects.get(pk=dm_line_pk)
    if request.user in dm_line.members.all():
        dm_line.delete()
    return redirect("messaging:view_dms")


def kick_from_group(request, group_pk, user_pk):
    group = MessagingGroup.objects.get(pk=group_pk)
    to_kick = CustomUser.objects.get(pk=user_pk)
    if request.user not in group.members.all():
        return render(request, "not_in_group.html")
    elif to_kick.is_superuser and not request.user.is_superuser:
        return render(request, "kick_admin.html")
    else:
        group.members.remove(to_kick)
        if to_kick.pk == request.user.pk:
            return redirect("messaging:view_chats")
        else:
            return redirect("messaging:view_chat", chat_pk=group_pk)


@user_passes_test(lambda user: user.is_superuser)
def ban_from_group(request, group_pk, user_pk):
    chat = MessagingGroup.objects.get(pk=group_pk)
    chat.members.remove(user_pk)
    chat.ban_list.add(user_pk)
    return redirect("messaging:view_chat", chat_pk=group_pk)
