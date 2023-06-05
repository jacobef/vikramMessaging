import rsa
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    public_key = models.BinaryField(null=True)
    private_key = models.BinaryField(null=True)
    profile_pic = models.ImageField(default="default_profile_pic.png")

    def in_database(self):
        return self.pk is not None

    def save(self, *args, **kwargs):
        if not self.in_database():
            public_key, private_key = rsa.newkeys(2048)
            self.public_key = public_key.save_pkcs1()
            self.private_key = private_key.save_pkcs1()
        return super().save(*args, **kwargs)


class MessagingGroup(models.Model):
    name = models.CharField(max_length=50)
    members = models.ManyToManyField(to=CustomUser, related_name="messaging_groups")
    read_list = models.ManyToManyField(to=CustomUser, related_name="groups_read")
    ban_list = models.ManyToManyField(to=CustomUser, related_name="banned_from")


class DirectMessageLine(models.Model):
    members = models.ManyToManyField(to=CustomUser, related_name="dm_lines")
    read_list = models.ManyToManyField(to=CustomUser, related_name="dm_lines_read")


class GroupMessage(models.Model):
    content = models.TextField(max_length=5000)
    by = models.ForeignKey(to=CustomUser, null=True, on_delete=models.SET_NULL, related_name="sent_gms")
    to = models.ForeignKey(to=MessagingGroup, on_delete=models.CASCADE, related_name="messages")
    time_sent = models.DateTimeField()


class DirectMessage(models.Model):
    content = models.BinaryField(max_length=2047)
    by = models.ForeignKey(to=CustomUser, null=True, on_delete=models.SET_NULL, related_name="sent_dms")
    to = models.ForeignKey(to=DirectMessageLine, null=True, on_delete=models.CASCADE, related_name="messages")
    time_sent = models.DateTimeField()
