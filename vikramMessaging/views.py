from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect


def create_account(request):
    if request.method == "GET":
        return render(request, "registration/create_account.html", {"form": UserCreationForm()})
    elif request.method == "POST":
        form = UserCreationForm(request.POST)
        form.save()
        return redirect("login")
