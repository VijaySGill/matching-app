from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
import os, json, operator
from datetime import datetime, date
from .models import UserProfile, Hobby, Likes

# Global scope
currentAccount = ""

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
        data = [{"success": False}]
        return JsonResponse(data, safe=False)

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def registerUser(request):
    #converts all usernames to lowercase so there are not multiple users with the same username is different cases
    username = (request.POST["username"]).lower()
    email = request.POST["email"]

    if(validateInput(username, email)):
        firstName = request.POST["firstName"]
        lastName = request.POST["lastName"]
        password = request.POST["password"]

        #checks that the date entered is 18 minimum
        dob = request.POST["dateOfBirth"]
        day,month,year = dob.split('-')
        today = date(int(day), int(month), int(year))
        age = calculate_age(today)
        if age<18:
            data = [{"success":"false", "message":"must be over 16"}]
            return JsonResponse(data, safe=False)

        #checks that at least one hobby has been selected
        hobbies = json.loads(request.POST['hobbies'])
        if not hobbies:
            data = [{"success":"false", "message":"no hobbies selected"}]
            return JsonResponse(data, safe=False)

        newUser = User.objects.create_user(username, email, password, first_name=firstName, last_name=lastName)
        newUser.save()

        userGender = request.POST["gender"]

        if request.FILES:
            image = request.FILES["profileImage"]
        else:
            image = "image/default.png"

        newProfile = UserProfile.objects.create(user=newUser, gender=userGender, dateOfBirth=dob, bio="", profileImage=image, likes=0)

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
    user = username.lower()
    if(User.objects.filter(username=user).exists()):
        return False
    else:
        return True

def checkEmail(email):
    if(User.objects.filter(email=email).exists()):
        return False
    else:
        return True

def validateInput(username, email):
    user = username.lower()
    if(checkUsername(user) and checkEmail(email)):
        return True
    else:
        return False

def login(request):
    #lets users enter username upper or lower case
    username = (request.POST["username"]).lower()
    password = request.POST["password"]
    try:
        user = User.objects.get(username=username)

        if(user.check_password(password)):
            request.session['username'] = username
            request.session['password'] = password

            currentAccount = username
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

def profile(request):
    return render(request,'matchingapp/profile.html')

def settingsPage(request):
    return render(request,'matchingapp/settings.html')

def loadUser(request):
    username = request.POST["username"]
    user = User.objects.get(username=username)
    userProfile = UserProfile.objects.get(user=user)
    hobbies = userProfile.hobby.all()

    userHobbies = []
    for hobby in hobbies:
        userHobbies.append(str(hobby))

    try:
        profileImage = userProfile.profileImage.url
    except:
        profileImage = None

    data = [{
        "success": "true",
        "id": user.id,
        "username": user.username,
        "firstName": user.first_name,
        "lastName": user.last_name,
        "dob": userProfile.dateOfBirth,
        "bio": userProfile.bio,
        "image": profileImage,
        "hobbies": userHobbies,
        "gender": userProfile.gender,
    }]
    return JsonResponse(data, safe=False)

def getProfiles(request):
    username = request.session['username']
    user = User.objects.get(username=username) # get me
    profiles = list(UserProfile.objects.all().values().exclude(user=user)) # get all profiles but mine
    users = list(User.objects.all().values().exclude(username=username)) # get all users but me
    content = {
        'profiles': profiles,
        'users': users,
    }
    return JsonResponse(content, safe=False)

def update(request):
    userID = request.POST['id']
    newUsername = request.POST['username']
    newFirstName = request.POST['firstName']
    newLastName = request.POST['lastName']
    newDOB = request.POST['dateOfBirth']
    newBio = request.POST['bio']
    newGender = request.POST['gender']

    user = User.objects.get(id=userID)
    profile = UserProfile.objects.get(user=user)

    user.username = newUsername
    user.first_name = newFirstName
    user.last_name = newLastName

    day,month,year = newDOB.split('-')
    today = date(int(day), int(month), int(year))
    age = calculate_age(today)
    if age<18:
        data = [{"success":"false"}]
        return JsonResponse(data, safe=False)

    profile.dateOfBirth = newDOB
    profile.bio = newBio
    profile.gender = newGender

    if request.FILES:
        profile.profileImage = request.FILES["profileImage"]

    user.save()
    profile.save()

    request.session['username'] = newUsername

    return JsonResponse({"success": True}, safe=False)

#deletes the user profile using the ID
@csrf_exempt
def delete(request):
    body = json.loads(request.body.decode('utf-8'))
    item = body['id']
    post = User.objects.get(id=item)
    post.delete()
    return HttpResponse("success")

def lookupMatches(request):
    count = 0;
    matches = {};

    myUsername = request.session['username']
    me = User.objects.get(username=myUsername)
    myProfile = UserProfile.objects.get(user=me)
    myHobbies = myProfile.hobby.all().values('name')

    theirProfiles = UserProfile.objects.all().exclude(user=me)
    for profile in theirProfiles:
        theirHobbies = profile.hobby.all().values('name')
        for theirHobby in theirHobbies:
            for myHobby in myHobbies:
                if(myHobby == theirHobby):
                    count = count + 1

        if(count == 0):
            matches[profile.user.username] = 0

        else:
            matches[profile.user.username] = count
        count = 0

    users = []
    userMatches = []
    userImages = []
    userProfiles = []
    sortedV = sorted(matches.items(), key=operator.itemgetter(1), reverse=True)
    for key in sortedV:
        name, theirMatches = key
        users.append(name)
        userMatches.append(theirMatches)

    for user in users:
        theUser = User.objects.get(username=user)
        theirProfile = UserProfile.objects.all().values().get(user=theUser)
        userProfiles.append(theirProfile)

    content = {
        'users': users,
        'profiles': userProfiles,
        'matches': userMatches
    }

    return JsonResponse(content, safe=False)

@csrf_exempt
def userLikes(request):
    body = json.loads(request.body.decode('utf-8'))
    item = body['username']

    #Creates a new user in the likes model if it doesn't exist already
    try:
        newUser = Likes.objects.create(name=item)
        newUser.save()
    except:
        print("already exists")

    newUser = Likes.objects.get(name=item)
    currentUser = User.objects.get(username=item)
    profile = UserProfile.objects.get(user=currentUser)

    likers = profile.profileLike.all()

    #if the user has already liked the profile and presses the button again it dislikes it
    for user in likers:
        if (str(user) == str(item)):
            profile.likes = profile.likes - 1
            profile.profileLike.remove(newUser)
            currentUser.save()
            profile.save()
            return HttpResponse("success")

    #if the likes has Nonetype, it initialises it with a value of 1
    if profile.likes:
        profile.profileLike.add(newUser)
        profile.likes = profile.likes + 1
    else:
        profile.profileLike.add(newUser)
        profile.likes = 1

    currentUser.save()
    profile.save()
    return HttpResponse("success")
