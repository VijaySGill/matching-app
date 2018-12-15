from django.urls import path

from . import views

urlpatterns = [
    path('home/', views.index, name='index'),
    path('authenticate/', views.authenticate, name='authenticate'),
    path('loginPage/', views.loginPage, name='loginPage'),
    path('registerUser/', views.registerUser, name='registerUser'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('getHobbies/', views.getHobbies, name='getHobbies'),
    path('lookupMatches/', views.lookupMatches, name='lookupMatches'),
    path('filterMatches/', views.filterMatches, name='filterMatches'),
    path('update/', views.update, name='update'),
    path('loadUser/', views.loadUser, name='loadUser'),
    path('profile/', views.profile, name="profile"),
    path('settings/', views.settingsPage, name="settings"),
    path('delete/', views.delete, name="delete"),
    path('getProfiles/', views.getProfiles, name="getProfiles"),
    path('userLikes/', views.userLikes, name="userLikes")

]
