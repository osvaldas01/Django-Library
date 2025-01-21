from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Books(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to="book_covers/")
    image_url = models.URLField(max_length=1000, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    pdf_file = models.FileField(upload_to='books/pdfs/', null=True, blank=True)
    topic = models.ForeignKey('Topic', on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    borrowed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='borrowed_books')
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_image_url(self):
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return '/static/images/default_book.png'

    class Meta:
        ordering = ['-updated', '-created']
        verbose_name_plural = "Books"

    def __str__(self):
        return self.title

    def get_book_content(self):
        if self.pdf_file:
            return self.pdf_file.url
        return self.content

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[0:50]
    
class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    EMOJI_MAP = {
        'add_book': '📚',
        'borrow_book': '📖',
        'return_book': '↩️',
        'delete_book': '🗑️',
        'update_book': '✏️',
    }

    def get_emoji(self):
        return self.EMOJI_MAP.get(self.activity_type, '📝')

    class Meta:
        ordering = ['-created']
        verbose_name_plural = "Activities"

    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"