import datetime

from django.db import models
from usercontrol_api.models import User


class Post(models.Model):
    class Type(models.TextChoices):
        CONFERENCE = ('conference', 'конференция')
        CONTEST = ('contest', 'конкурс')
        EXCURSION = ('excursion', 'экскурсия')
        SEMINAR = ('seminar', 'семинар')

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.CONFERENCE)
    event_date = models.DateTimeField(default=datetime.datetime.now)
    description = models.TextField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Post by %s - %s - %s" % (self.author.username, self.type, self.event_date)


class PostPhoto(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='photo/')
    description = models.TextField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Photo for post #%s" % self.post.id


class PostVideo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='video/')
    description = models.TextField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Video for post #%s" % self.post.id
