from django.urls import path
from messaging import views

app_name = "messaging"

urlpatterns = [
    path("", views.view_chats, name="view_chats"),
    path("<int:chat_pk>/", views.view_chat, name="view_chat"),
    path("<int:chat_pk>/invite/", views.invite, name="invite"),
]