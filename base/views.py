from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseNotAllowed       
from .models import Books, Topic, Message, Activity
from .forms import BookForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
import requests
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
import tempfile
import os
import re
from tempfile import NamedTemporaryFile
from django.core.files.base import File


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
    q = request.GET.get('q', '')
    topic_name = request.GET.get('topic', '')
    
    books = Books.objects.all()
    
    # Apply topic filter
    if topic_name:
        books = books.filter(topic__name=topic_name)
    
    # Apply search filter
    if q:
        books = books.filter(
            Q(title__icontains=q) |
            Q(author__icontains=q) |
            Q(topic__name__icontains=q)
        )
    
    topics = Topic.objects.all()
    
    context = {
        'books': books,
        'topics': topics,
        'topic_name': topic_name,
    }
    return render(request, 'base/home.html', context)

def book(request, pk):
    book = Books.objects.get(id=pk)
    bookMessages = book.message_set.all().order_by('-created')

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            book = book,
            body = request.POST.get('body')
        )

        Activity.objects.create(
            user = request.user,
            activity_type = 'comment',
            description = f"Commented on {book.title}"
        )
        return redirect('book', pk=book.id)

    context = {'book': book, 'bookMessages':bookMessages}
    return render(request, "base/book.html", context)

@login_required(login_url='login')
def createBook(request):
    form = BookForm()
    
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user
            
            # Handle image upload
            if 'image' in request.FILES:
                book.image = request.FILES['image']
                book.image_url = None  # Clear any existing image URL if uploading new image
            
            book.save()
            return redirect('home')
            
    context = {'form': form}
    return render(request, 'base/book_form.html', context)

@login_required(login_url='login')
def borrowBook(request, pk):
    book = get_object_or_404(Books, id=pk)
    
    if book.available:
        book.available = False
        book.borrowed_by = request.user  # Set the borrowed_by field
        book.save()
        
        Activity.objects.create(
            user=request.user,
            activity_type='borrow_book',
            description=f'Borrowed book: {book.title}'
        )
        
        messages.success(request, f'You have successfully borrowed {book.title}')
    else:
        messages.error(request, 'This book is not available for borrowing')
    
    return redirect('book', pk=pk)

@login_required(login_url='login')
def returnBook(request, pk):
    book = get_object_or_404(Books, id=pk)
    
    if request.user == book.borrowed_by:
        book.available = True
        book.borrowed_by = None
        book.save()
        
        Activity.objects.create(
            user=request.user,
            activity_type='return_book',
            description=f'Returned book: {book.title}'
        )
        
        messages.success(request, f'You have successfully returned {book.title}')
    else:
        messages.error(request, 'You cannot return this book as you did not borrow it')
    
    return redirect('book', pk=pk)

@login_required(login_url='login')
def updateBook(request, pk):
    book = Books.objects.get(id=pk)
    form = BookForm(instance=book)
    
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            # Handle image upload
            if 'image' in request.FILES:
                book.image = request.FILES['image']
                book.image_url = None  # Clear any existing image URL if uploading new image
            
            form.save()
            return redirect('home')
            
    context = {'form': form}
    return render(request, 'base/book_form.html', context)

@login_required(login_url='login')
def deleteBook(request, pk):
    book = Books.objects.get(id=pk)

    if not (request.user == book.user or request.user.is_staff):
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        book.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': book})

@login_required(login_url='login')
def userProfile(request):
    user = request.user
    activities = Activity.objects.filter(user=user).order_by('-created')[:10]  # Get last 10 activities
    context = {
        'user': user,
        'activities': activities,
        'borrowed_books': user.borrowed_books.all(),
        'added_books': user.books_set.all(),
    }
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def editProfile(request):
    user = request.user
    
    if request.method == 'POST':
        # Handle password change
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password:
            if not user.check_password(current_password):
                messages.error(request, 'Current password is incorrect')
                return redirect('edit-profile')
            
            if new_password != confirm_password:
                messages.error(request, 'New passwords do not match')
                return redirect('edit-profile')
            
            user.set_password(new_password)
        
        # Update user information
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()
        
        messages.success(request, 'Profile updated successfully')
        return redirect('profile', pk=user.id)
    
    return render(request, 'base/edit_profile.html', {'user': user})

@staff_member_required
def scrapeBooks(request):
    books = []
    if 'query' in request.GET:
        query = request.GET.get('query')
        limit = int(request.GET.get('limit', 5))
        
        try:
            google_url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={limit}"
            response = requests.get(google_url)
            data = response.json()
            
            if 'items' in data:
                for item in data['items']:
                    volume_info = item.get('volumeInfo', {})
                    image_links = volume_info.get('imageLinks', {})
                    image_url = (image_links.get('thumbnail') or 
                               image_links.get('smallThumbnail') or 
                               '/static/images/default_book.png')
                    
                    if image_url.startswith('http:'):
                        image_url = 'https:' + image_url[5:]
                    
                    # Get categories from Google Books API
                    categories = volume_info.get('categories', [])
                    # Use the first category or default to "Other"
                    topic_name = categories[0] if categories else "Other"
                    topic, _ = Topic.objects.get_or_create(name=topic_name)
                    
                    description = volume_info.get('description', 'No description available.')
                    content = description
                    
                    books.append({
                        'title': volume_info.get('title', 'Unknown Title'),
                        'author': ', '.join(volume_info.get('authors', ['Unknown Author'])),
                        'description': description,
                        'image_url': image_url,
                        'content': content,
                        'topic': topic
                    })

        except Exception as e:
            messages.error(request, f'Error searching for books: {str(e)}')

    if request.method == 'POST':
        if 'bulk_import' in request.POST:
            selected_titles = request.POST.getlist('selected_books')
            
            for title in selected_titles:
                try:
                    # Find matching book data
                    book_data = next((b for b in books if b['title'] == title), None)
                    
                    if book_data:
                        # Create book
                        book = Books.objects.create(
                            title=book_data['title'],
                            author=book_data['author'],
                            description=book_data['description'],
                            content=book_data['content'],
                            user=request.user,
                            topic=book_data['topic'],
                            available=True
                        )

                        # Handle image
                        if book_data['image_url'] and book_data['image_url'] != '/static/images/default_book.png':
                            try:
                                response = requests.get(book_data['image_url'])
                                if response.status_code == 200:
                                    img_temp = NamedTemporaryFile(delete=True)
                                    img_temp.write(response.content)
                                    img_temp.flush()
                                    book.image.save(f"book_{book.id}.jpg", File(img_temp))
                            except Exception:
                                pass

                        # Create activity
                        Activity.objects.create(
                            user=request.user,
                            activity_type='add_book',
                            description=f'Added book: {book.title}'
                        )
                        messages.success(request, f'Successfully imported: {book.title}')
                        
                except Exception as e:
                    messages.error(request, f'Error importing {title}: {str(e)}')
            
            return redirect('home')

    context = {
        'books': books,
        'query': request.GET.get('query', ''),
        'limit': request.GET.get('limit', 5)
    }
    return render(request, 'base/scrape_books.html', context)

@staff_member_required
def importBook(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        description = request.POST.get('description')
        category = request.POST.get('category')
        image_url = request.POST.get('image_url')
        text_url = request.POST.get('text_url')
        source = request.POST.get('source')
        
        try:
            topic = Topic.objects.get_or_create(name=category)[0]
            
            # Get the text content for Gutenberg books
            content = None
            if source == 'gutenberg':
                try:
                    response = requests.get(text_url)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Find the main content
                    main_content = soup.find('body')
                    if main_content:
                        content = str(main_content)
                except Exception as e:
                    messages.warning(request, f'Error fetching book content: {str(e)}')
            
            book = Books.objects.create(
                title=title,
                author=author,
                description=description,
                user=request.user,
                topic=topic,
                image_url=image_url,
                content=content
            )
            
            messages.success(request, f'Successfully imported: {title}')
            
            Activity.objects.create(
                user=request.user,
                activity_type='add_book',
                description=f'Imported book: {title} (Category: {category})'
            )
            
            return redirect('book', pk=book.id)
            
        except Exception as e:
            messages.error(request, f'Error importing book: {str(e)}')
            return redirect('scrape-books')
    
    return redirect('scrape-books')

@login_required(login_url='login')
def readBook(request, pk):
    book = get_object_or_404(Books, id=pk)
    
    # Check if book has content
    if not book.pdf_file and not book.content:
        messages.error(request, 'This book has no content available.')
        return redirect('book', pk=book.id)
    
    context = {'book': book}
    return render(request, 'base/read_book.html', context)