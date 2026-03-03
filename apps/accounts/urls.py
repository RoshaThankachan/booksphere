from django.urls import path
from .views import signup_view, login_view, logout_view, dashboard, profile_detail, profile_update, download_history, user_reviews

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/', profile_detail, name='profile_detail'),
    path('profile/edit/', profile_update, name='profile_update'),
    path('history/', download_history, name='download_history'),
    path('reviews/', user_reviews, name='user_reviews'),
]
