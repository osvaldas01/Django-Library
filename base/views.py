from django.shortcuts import render, redirect
from django.http import HttpResponse       
from .models import Books
from .forms import BookForm


def home(request):
    books = Books.objects.all()
    context = {"books":books}
    return render(request, "base/home.html", context)

def book(request, pk):
    book = Books.objects.get(id=pk)
    context = {'book': book}
    return render(request, "base/book.html", context)

def addBook(request):
    form = BookForm()

    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/book_form.html', context)


def updateBook(request, pk):
    book = Books.objects.get(id=pk)
    form = BookForm(instance=book)

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/book_form.html', context)

def deleteBook(request, pk):
    book = Books.objects.get(id=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': book})