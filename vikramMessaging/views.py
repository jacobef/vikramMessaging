from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

@login_required
def home(request):
    return render(request, "home.html")

def create_account(request):
    if request.method == "GET":
        return render(request, "registration/create_account.html", {"form": UserCreationForm()})
    elif request.method == "POST":
        form = UserCreationForm(request.POST)
        form.save()
        return redirect("login")
