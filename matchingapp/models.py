from django.db import models
from django.contrib.auth.models import User

'''Hobby model stores the name of the different hobbies'''
class Hobby(models.Model):
    name = models.CharField(max_length=30, blank=False, unique=True)

    def __str__(self):
        return self.name

'''Likes model stores the name of the user being liked'''
class Likes(models.Model):
    name = models.CharField(max_length=100,blank=True, null=True, unique=True)

    def __str__(self):
        return self.name

'''UserProfile model for the matchingapp. We used the django contib auth model for the User model, and used a one-to-one relationship to map each profile to their user in order to store additional information such as gender, date of birth, their biography, profile image, and likes they had been given. A many-to-many relationship is also used here to map each UserProfile to their hobbies'''
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=6, blank=False)
    dateOfBirth = models.DateField(null=True, blank=False)
    bio = models.TextField(max_length=500, blank=True)
    profileImage = models.ImageField(upload_to="image", blank=True, null=True)
    hobby = models.ManyToManyField(Hobby, blank=False)
    profileLike = models.ManyToManyField(Likes, blank=False) #the profiles the user has liked
    likes = models.FloatField(null=True, blank=False) #the total number of likes the user has

    def __str__(self):
        return self.user.get_username()
