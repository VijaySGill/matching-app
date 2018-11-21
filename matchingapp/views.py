from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json

from .models import UserProfile, Hobby

def index(request):
    return render(request,'matchingapp/home.html')

def loginPage(request):
    return render(request, 'matchingapp/login.html')

def register(request):
    return render(request,'matchingapp/register.html')

def getHobbies(request):
    hobbies = list(Hobby.objects.all().values())
    return JsonResponse(hobbies, safe=False)

@csrf_exempt
def authenticate(request):
    if 'username' in request.session:
        data = [{"success":True, "username":request.session['username']}]
        return JsonResponse(data, safe=False)

    else:
        data = [{"success":"false"}]
        return JsonResponse(data, safe=False)

@csrf_exempt
def registerUser(request):
    username = request.POST["username"]
    email = request.POST["email"]

    if(validateInput(username, email)):
        firstName = request.POST["firstName"]
        lastName = request.POST["lastName"]
        password = request.POST["password"]

        hobbies = json.loads(request.POST['hobbies'])
        if not hobbies:
            data = [{"success":"false", "message":"no hobbies selected"}]
            return JsonResponse(data, safe=False)

        newUser = User.objects.create_user(username, email, password, first_name=firstName, last_name=lastName)
        newUser.save()

        dob = request.POST["dateOfBirth"]
        userGender = request.POST["gender"]

        newProfile = UserProfile.objects.create(user=newUser, gender=userGender, dateOfBirth=dob, bio="")

        for hobby in hobbies:
            userHobby = Hobby.objects.get(name=hobby)
            newProfile.hobby.add(userHobby)

        request.session['username'] = username
        request.session['password'] = password

        data = [{"success":"true"}]
        return JsonResponse(data, safe=False)

    else:
        data = [{"success":"false", "message":"user or email taken"}]
        return JsonResponse(data, safe=False)

def checkUsername(username):
    if(User.objects.filter(username=username).exists()):
        return False

    else:
        return True

def checkEmail(email):
    if(User.objects.filter(email=email).exists()):
        return False

    else:
        return True

def validateInput(username, email):
    if(checkUsername(username) and checkEmail(email)):
        return True

    else:
        return False

@csrf_exempt
def login(request):
    username = request.POST["username"]
    password = request.POST["password"]

    try:
        user = User.objects.get(username=username)

        if(user.check_password(password)):
            request.session['username'] = username
            request.session['password'] = password

            data = [{"success":"true","username": username}]
            return JsonResponse(data, safe=False)

        else:
            data = [{"success":"false",  "message": "incorrect password"}]
            return JsonResponse(data, safe=False)

    except User.DoesNotExist:
        data = [{"success":"false",  "message": "user does not exist"}]
        return JsonResponse(data, safe=False)

@csrf_exempt
def logout(request):
    if 'username' in request.session:
        request.session.flush()
        print("---------USER LOGGED OUT------------------")
        data = [{"success":"true"}]

        return JsonResponse(data, safe=False)

    else:
        data = [{"success":"false"}]
        return JsonResponse(data, safe=False)
