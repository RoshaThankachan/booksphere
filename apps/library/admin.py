from django.contrib import admin

# Register your models here.
from .models import Genre,Author,Book,Review

admin.site.register(Genre)
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Review)