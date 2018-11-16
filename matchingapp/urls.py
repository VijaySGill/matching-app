from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('registerUser/', views.registerUser, name='registerUser'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('getHobbies/', views.getHobbies, name='getHobbies'),

]
