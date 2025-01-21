from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerUser, name="register"),
    path("", views.home, name="home"),
    path("book/<str:pk>/", views.book, name="book"),
    path('add-book/', views.addBook, name="add-book"),
    path('update-book/<str:pk>/', views.updateBook, name="update-book"),
    path('delete-book/<str:pk>/', views.deleteBook, name="delete-book"),
    path('borrow-book/<str:pk>/', views.borrowBook, name="borrow-book"),

]