from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('authenticate/', views.authenticate, name='authenticate'),
    path('loginPage/', views.loginPage, name='loginPage'),
    path('registerUser/', views.registerUser, name='registerUser'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('getHobbies/', views.getHobbies, name='getHobbies'),

]
