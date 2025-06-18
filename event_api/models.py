import datetime

from django.db import models
from usercontrol_api.models import User, Group


class Event(models.Model):
    class Type(models.TextChoices):
        CONFERENCE = ('conference', 'конференция')
        CONTEST = ('contest', 'конкурс')
        EXCURSION = ('excursion', 'экскурсия')
        SEMINAR = ('seminar', 'семинар')

    title = models.CharField(max_length=128)
    description = models.TextField(max_length=500, blank=True, null=True)
    location = models.CharField(max_length=128)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    max_attendees = models.PositiveIntegerField(default=100, blank=True, null=True)
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.CONFERENCE)
    event_date = models.DateTimeField(default=datetime.datetime.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def attendees(self):
        if self.group:
            return User.objects.filter(group=self.group).count()
        return 0


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Post by %s - %s - %s" % (self.author.username, self.type, self.event_date)


class EventPhoto(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='photo/')
    description = models.TextField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Photo for post #%s" % self.event.id


class EventVideo(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='video/')
    description = models.TextField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Video for post #%s" % self.event.id
