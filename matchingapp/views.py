from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from .models import UserProfile, Hobby

def index(request):
    return render(request,'matchingapp/register.html')

def getHobbies(request):
    hobbies = list(Hobby.objects.all().values())
    return JsonResponse(hobbies, safe=False)

@csrf_exempt
def registerUser(request):
    username = request.POST["username"]
    email = request.POST["email"]

    User.objects.filter(username=username).exists()
    User.objects.filter(email=email).exists()

    firstName = request.POST["firstName"]
    lastName = request.POST["lastName"]
    password = request.POST["password"]

    newUser = User.objects.create_user(username, email, password, first_name=firstName, last_name=lastName)
    newUser.save()

    dob = request.POST["dateOfBirth"]
    userGender = request.POST["gender"]
    UserProfile.objects.create(user=newUser, gender=userGender, dateOfBirth=dob, bio="")

        # request.session['username'] = username
        # request.session['password'] = password

    data = [{"success":"true"}]
    return JsonResponse(data, safe=False)
