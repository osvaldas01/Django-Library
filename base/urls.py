from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerUser, name="register"),
    path('profile/', views.userProfile, name='profile'),
    path("", views.home, name="home"),
    path("book/<str:pk>/", views.book, name="book"),
    path('add-book/', views.createBook, name="add-book"),
    path('update-book/<str:pk>/', views.updateBook, name="update-book"),
    path('delete-book/<str:pk>/', views.deleteBook, name="delete-book"),
    path('borrow-book/<str:pk>/', views.borrowBook, name="borrow-book"),
    path('edit-profile/', views.editProfile, name='edit-profile'),
    path('scrape-books/', views.scrapeBooks, name='scrape-books'),
    path('import-books/', views.importBook, name='import-books'),
    path('book/<str:pk>/read/', views.readBook, name='read-book'),
    path('book/<str:pk>/return/', views.returnBook, name='return-book'),
]