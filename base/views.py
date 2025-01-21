from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseNotAllowed       
from .models import Books, Topic, Message
from .forms import BookForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm


def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Username or Password does not exist')

    context = {'page':page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Something went wrong')

    return render(request, 'base/login_register.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    books = Books.objects.filter(
        Q(topic__name__icontains=q) |
        Q(title__icontains=q) |
        Q(series__icontains=q)
        )

    topics = Topic.objects.all()
    books_count = books.count()

    context = {"books":books, "topics":topics, "books_count": books_count}
    return render(request, "base/home.html", context)

def book(request, pk):
    book = Books.objects.get(id=pk)
    bookMessages = book.message_set.all().order_by('-created')

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            book = book,
            body = request.POST.get('body')
        )
        return redirect('book', pk=book.id)

    context = {'book': book, 'bookMessages':bookMessages}
    return render(request, "base/book.html", context)

@login_required(login_url='login')
def addBook(request):
    form = BookForm()

    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/book_form.html', context)

@login_required(login_url='login')
def borrowBook(request, pk):
    book = get_object_or_404(Books, id=pk)

    if request.method == 'POST':
        if book.available:
            book.available = False
            book.save()
            messages.success(request, 'You have successfully borrowed the book.')
        else:
            messages.error(request, 'Book is not available for borrowing.')
            return render(request, 'base/borrow_book.html', {'obj': book})
        
    return render(request, 'base/borrow_book.html', {'obj': book})


@login_required(login_url='login')
def updateBook(request, pk):
    book = Books.objects.get(id=pk)
    form = BookForm(instance=book)

    if request.user != book.user:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/book_form.html', context)

@login_required(login_url='login')
def deleteBook(request, pk):
    book = Books.objects.get(id=pk)

    if request.user != book.user:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        book.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': book})