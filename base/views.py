from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseNotAllowed       
from .models import Books, Topic
from .forms import BookForm
from django.contrib import messages


def home(request):
    books = Books.objects.all()

    topics = Topic.objects.all()

    context = {"books":books, "topics":topics}
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