from django.db import models
from django.contrib.auth.models import User
from apps.library.models import Book

class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    members = models.ManyToManyField(User, related_name='book_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Sharing(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_books')
    available_for_loan = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.book.title} shared by {self.owner.username}"

class Discussion(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='discussions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Discussion by {self.user.username} in {self.group.name}"
