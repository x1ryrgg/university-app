from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=10, default='new group')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = ('student', 'Студент')
        TEACHER = ('teacher', 'Преподаватель')

    email = models.EmailField()
    role = models.CharField(max_length=7, choices=Role, default=Role.TEACHER)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, null=True, related_name='students')
    tg_id = models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return '%s (%s) - %s' % (self.username, self.group, self.role)

