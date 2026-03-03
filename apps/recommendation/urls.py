from django.urls import path
from . import views

app_name = 'recommendation'

urlpatterns = [
    path('', views.recommendations_home, name='home'),
    path('mood/', views.recommendations_by_mood, name='mood'),
    path('genre/<int:genre_id>/', views.genre_recommendations, name='by_genre'),
]
