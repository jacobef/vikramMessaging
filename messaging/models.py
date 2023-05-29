from django.contrib.auth.models import User, AbstractUser
from django.db import models


class MessagingGroup(models.Model):
    name = models.CharField(max_length=50)
    members = models.ManyToManyField(to=User, related_name="messaging_groups")
    read_list = models.ManyToManyField(to=User, related_name="groups_read")


class DirectMessageLine(models.Model):
    members = models.ManyToManyField(to=User, related_name="dm_lines")
    read_list = models.ManyToManyField(to=User, related_name="dm_lines_read")


class GroupMessage(models.Model):
    content = models.TextField(max_length=5000)
    by = models.ForeignKey(to=User, null=True, on_delete=models.SET_NULL, related_name="sent_gms")
    to = models.ForeignKey(to=MessagingGroup, on_delete=models.CASCADE, related_name="messages")
    time_sent = models.DateTimeField()


class DirectMessage(models.Model):
    content = models.TextField(max_length=5000)  # Upgrade later
    by = models.ForeignKey(to=User, null=True, on_delete=models.SET_NULL, related_name="sent_dms")
    to = models.ForeignKey(to=DirectMessageLine, null=True, on_delete=models.SET_NULL, related_name="messages")
    time_sent = models.DateTimeField()
