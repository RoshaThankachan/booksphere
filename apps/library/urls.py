from django.urls import path
from .views import book_list, book_detail, toggle_favorite, favorites_list

urlpatterns = [
    path('', book_list, name='book_list'),
    path('favorites/', favorites_list, name='favorites_list'),
    path('toggle-favorite/<int:pk>/', toggle_favorite, name='toggle_favorite'),
    path('<int:pk>/', book_detail, name='book_detail'),
]
