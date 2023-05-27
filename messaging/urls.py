from django.urls import path
from messaging import views

app_name = "messaging"

urlpatterns = [
    path("gcs/", views.view_chats, name="view_chats"),
    path("gcs/<int:chat_pk>/", views.view_chat, name="view_chat"),
    path("gcs/<int:chat_pk>/invite/", views.invite, name="invite"),
    path("gcs/<int:chat_pk>/leave/", views.leave_chat, name="leave_chat"),
    path("gcs/new/", views.NewChat.as_view(), name="new_chat"),

    path("dms/", views.view_dms, name="view_dms"),
    path("dms/<int:user_pk>/", views.view_dm, name="view_dm"),
    path("dms/message/<int:dm_pk>/delete", views.delete_dm, name="delete_dm"),
]