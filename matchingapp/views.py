from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.forms.models import model_to_dict
import os, json, operator
from datetime import datetime, date
from .models import UserProfile, Hobby, Likes

#global scope
currentAccount = ""

'''Returns and renders the page that is requested'''
def index(request):
    return render(request,'matchingapp/home.html')

def loginPage(request):
    return render(request, 'matchingapp/login.html')

def register(request):
    return render(request,'matchingapp/register.html')

def profile(request):
    return render(request,'matchingapp/profile.html')

def settingsPage(request):
    return render(request,'matchingapp/settings.html')


'''Makes a list of all the hobbies in a readable format'''
def getHobbies(request):
    hobbies = list(Hobby.objects.all().values())
    return JsonResponse(hobbies, safe=False)

'''Checks that the username passed is in the current session'''
@csrf_exempt
def authenticate(request):
    if 'username' in request.session:
        data = [{"success":True, "username":request.session['username']}]
        return JsonResponse(data, safe=False)

    else:
        data = [{"success": False}]
        return JsonResponse(data, safe=False)

'''Calculates the age of the user'''
def calculateAge(DOB):
    today = date.today()
    return today.year - DOB.year - ((today.month, today.day) < (DOB.month, DOB.day))

'''Registers a new user and does validation checks on the data inputted'''
def registerUser(request):

    #converts all usernames to lowercase so there are not multiple users with the same username in different cases
    username = (request.POST["username"]).lower()
    email = request.POST["email"]

    if(validateInput(username, email)):
        firstName = request.POST["firstName"]
        lastName = request.POST["lastName"]
        password = request.POST["password"]

        #checks that the user is at least 18 years old
        dob = request.POST["dateOfBirth"]
        day,month,year = dob.split('-')
        DOB = date(int(day), int(month), int(year))
        age = calculateAge(DOB)
        if age<18:
            data = [{"success":"false", "message":"must be over 18"}]
            return JsonResponse(data, safe=False)

        #checks that at least one hobby has been selected
        hobbies = json.loads(request.POST['hobbies'])
        if not hobbies:
            data = [{"success":"false", "message":"no hobbies selected"}]
            return JsonResponse(data, safe=False)

        newUser = User.objects.create_user(username, email, password, first_name=firstName, last_name=lastName)
        newUser.save()

        userGender = request.POST["gender"]

        #uses a default image if no file is uploaded by the user
        if request.FILES:
            image = request.FILES["profileImage"]
        else:
            image = "image/default.png"

        newProfile = UserProfile.objects.create(user=newUser, gender=userGender, dateOfBirth=dob, bio="", profileImage=image, likes=0)

        for hobby in hobbies:
            userHobby = Hobby.objects.get(name=hobby)
            newProfile.hobby.add(userHobby)

        #stores current user in session cache
        request.session['username'] = username
        request.session['password'] = password

        data = [{"success":"true"}]
        return JsonResponse(data, safe=False)

    else:
        data = [{"success":"false", "message":"user or email taken"}]
        return JsonResponse(data, safe=False)

'''Checks if the username is in the database already'''
def checkUsername(username):
    user = username.lower()
    if(User.objects.filter(username=user).exists()):
        return False
    else:
        return True

'''Checks if the email is in the database already'''
def checkEmail(email):
    if(User.objects.filter(email=email).exists()): #Checks if the email is in the database already
        return False
    else:
        return True

'''Checks that the email and username are not already in the database'''
def validateInput(username, email):
    user = username.lower()
    if(checkUsername(user) and checkEmail(email)):
        return True
    else:
        return False

'''Validates the login details of the user'''
def login(request):
    #lets users enter their username in upper or lower case
    username = (request.POST["username"]).lower()
    password = request.POST["password"]
    try:
        user = User.objects.get(username=username)
        #checks that the password matches username
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

'''Logs the user out by getting rid of user information held in memory'''
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

'''Loads information about a specific user'''
def loadUser(request):
    username = request.POST["username"]
    user = User.objects.get(username=username)
    userProfile = UserProfile.objects.get(user=user)
    hobbies = userProfile.hobby.all()

    userHobbies = [] #loops through hobbies and stores them in an array to pass back to frontend
    for hobby in hobbies:
        userHobbies.append(str(hobby))

    try: #gets the image path stored
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
        "likes": userProfile.likes
    }]
    return JsonResponse(data, safe=False)

'''Gets all the profiles of other users (excluding the user who is currently logged in)'''
def getProfiles(request):
    username = request.session['username']
    user = User.objects.get(username=username)
    profiles = list(UserProfile.objects.all().values().exclude(user=user))
    users = list(User.objects.all().values().exclude(username=username))
    content = {
        'profiles': profiles,
        'users': users,
    }
    return JsonResponse(content, safe=False)

'''Updates information about a specific user with new data'''
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
    #sets each field with the new information from the form
    user.username = newUsername
    user.first_name = newFirstName
    user.last_name = newLastName
    profile.dateOfBirth = newDOB
    profile.bio = newBio
    profile.gender = newGender

    if request.FILES: #if file has a new image then it overwrites the field, else theres no change
        profile.profileImage = request.FILES["profileImage"]

    user.save()
    profile.save()

    request.session['username'] = newUsername

    return JsonResponse({"success": True}, safe=False)

'''Deletes the user profile using their ID'''
@csrf_exempt
def delete(request):
    body = json.loads(request.body.decode('utf-8'))
    item = body['id']
    post = User.objects.get(id=item)
    post.delete()
    return HttpResponse("success")

'''Returns a list of other profiles after sorting them by the number of hobby matches'''
def lookupMatches(request):
    count = 0;
    matches = {};

    myUsername = request.session['username']
    me = User.objects.get(username=myUsername)
    myProfile = UserProfile.objects.get(user=me)
    myHobbies = myProfile.hobby.all().values('name')
    myLikes = myProfile.profileLike.all().values('name')

    #compares the logged in user's hobbies with other users and counts the number of matches there are
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

    theirProfiless = UserProfile.objects.all()
    for profile in theirProfiless:
        likes = profile.profileLike.all()

    users = []
    userMatches = []
    userImages = []
    userProfiles = []
    sortedV = sorted(matches.items(), key=operator.itemgetter(1), reverse=True) #sorts the user profiles depending on the number of matches
    for key in sortedV:
        name, theirMatches = key
        users.append(name)
        userMatches.append(theirMatches)

    liked = []
    for likes in myLikes:
        l = likes.get('name')
        liked.append(l)

    for user in users:
        theUser = User.objects.get(username=user)
        theirProfile = UserProfile.objects.all().values().get(user=theUser)
        userProfiles.append(theirProfile)

    content = {
        'users': users,
        'profiles': userProfiles,
        'matches': userMatches,
        'likes': liked
    }

    return JsonResponse(content, safe=False)

'''Filters the profiles displayed depending on gender and age restrictions'''
def filterMatches(request):
    count = 0;
    matches = {};

    myUsername = request.session['username']
    gender = request.POST['gender']
    age1 = request.POST['age1']
    age2 = request.POST['age2']

    me = User.objects.get(username=myUsername)
    myProfile = UserProfile.objects.get(user=me)
    myHobbies = myProfile.hobby.all().values('name')
    myLikes = myProfile.profileLike.all().values('name')

    theirProfiles = UserProfile.objects.filter(gender=gender).exclude(user=me)

    for profile in theirProfiles:
        theirAge = calculateAge(profile.dateOfBirth)
        if not(theirAge >= int(age1) and theirAge <= int(age2)):
            theirProfiles = theirProfiles.exclude(id=profile.id)

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

    liked = []
    for likes in myLikes:
        l = likes.get('name')
        liked.append(l)

    for user in users:
        theUser = User.objects.get(username=user)
        theirProfile = UserProfile.objects.all().values().get(user=theUser)
        userProfiles.append(theirProfile)

    content = {
        'users': users,
        'profiles': userProfiles,
        'matches': userMatches,
        'likes': liked
    }

    return JsonResponse(content, safe=False)


'''Keeps track of profile likes'''
@csrf_exempt
def userLikes(request):
    body = json.loads(request.body.decode('utf-8'))
    likedThemUsername = body['username']
    likerMeUsername = request.session['username']

    #creates a new user in the likes model if it doesn't exist already (person being liked)
    try:
        newUser = Likes.objects.create(name=likedThemUsername)
        newUser.save()
    except:
        print("already exists")

    #me
    likerMeUser = User.objects.get(username=likerMeUsername)
    likeMeProfile = UserProfile.objects.get(user=likerMeUser)
    liked = likeMeProfile.profileLike.all() #the profiles I have liked

    #the profile being liked
    newUser = Likes.objects.get(name=likedThemUsername)
    likedThemUser = User.objects.get(username=likedThemUsername)
    likedThemProfile = UserProfile.objects.get(user=likedThemUser)

    #if the user has already liked the profile and presses the button again it dislikes it and removes the user being disliked from the users profileLike list
    for user in liked:
        if (str(user) == str(likedThemUsername)):
            likedThemProfile.likes = likedThemProfile.likes - 1
            likeMeProfile.profileLike.remove(newUser)
            likedThemProfile.save()
            likeMeProfile.save()
            return JsonResponse({"success": "False"}, safe=False)

    #if the likes has Nonetype, it initialises it with a value of 1
    if likedThemProfile.likes:
        likeMeProfile.profileLike.add(newUser)
        likedThemProfile.likes = likedThemProfile.likes + 1
    else:
        likeMeProfile.profileLike.add(newUser)
        likedThemProfile.likes = 1

    likedThemProfile.save()
    likeMeProfile.save()
    return JsonResponse({"success": "True"}, safe=False)

'''Allows users to change their password'''
def updatePassword(request):
    myUsername = request.session['username']
    currentPassword = request.POST['currentPassword']
    newPassword = request.POST['newPassword']

    user = User.objects.get(username=myUsername)
    if(user.check_password(currentPassword)):
        user.password = make_password(newPassword)
        user.save()
        print("-------DONE-------------")
        data = {"success":True}
        return JsonResponse(data, safe=False)
    else:
        print("-------No match!-------------")
        data = {"success":False}
        return JsonResponse(data, safe=False)
