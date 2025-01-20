from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("book/<str:pk>/", views.book, name="book"),
    path('add-book/', views.addBook, name="add-book"),
    path('update-book/<str:pk>/', views.updateBook, name="update-book"),
    path('delete-book/<str:pk>/', views.deleteBook, name="delete-book"),

]