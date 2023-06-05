from django.urls import path
from messaging import views

app_name = "messaging"

urlpatterns = [
    path("gcs/", views.view_chats, name="view_chats"),
    path("gcs/<int:chat_pk>/", views.view_chat, name="view_chat"),
    path("gcs/message/<int:gm_pk>/delete/", views.delete_gm, name="delete_gm"),
    path("gcs/<int:chat_pk>/invite/", views.invite, name="invite"),
    path("gcs/<int:chat_pk>/leave/", views.leave_chat, name="leave_chat"),
    path("gcs/new/", views.NewChat.as_view(), name="new_chat"),

    path("dms/", views.view_dms, name="view_dms"),
    path("dms/<int:dm_line_pk>/", views.view_dm_line, name="view_dm_line"),
    path("dms/<int:group_pk>/kick/<int:user_pk>/", views.kick_from_group, name="kick_from_group"),
    path("dms/<int:group_pk>/ban/<int:user_pk>/", views.ban_from_group, name="ban_from_group"),
    path("dms/<int:group_pk>/unban/<int:user_pk>/", views.unban_from_group, name="unban_from_group"),
    path("dms/<int:dm_line_pk>/delete/", views.delete_dm_line, name="delete_dm_line"),
    path("dms/message/<int:dm_pk>/delete/", views.delete_dm, name="delete_dm"),
    path("dms/new/", views.new_dm_line, name="new_dm_line")
]