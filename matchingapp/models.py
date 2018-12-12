from django.db import models
from django.contrib.auth.models import User
from .upload import UploadTo

class Hobby(models.Model):
    name = models.CharField(max_length=30, blank=False, unique=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=6, blank=False)
    dateOfBirth = models.DateField(null=True, blank=False)
    bio = models.TextField(max_length=500, blank=True)
    profileImage = models.ImageField(upload_to="image", blank=True, null=True)
    hobby = models.ManyToManyField(Hobby, blank=False)

    def __str__(self):
        return self.user.get_username()
