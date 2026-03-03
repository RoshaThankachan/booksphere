from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .utils import (
    generate_personalized_recommendations,
    get_genre_based_recommendations,
    get_reading_history_recommendations,
    get_highly_rated_by_category,
    get_popular_books,
    get_mood_based_recommendations
)
from apps.library.models import Genre, Issue, Review


@login_required
def recommendations_home(request):
    """Main recommendations page showing personalized suggestions."""
    user = request.user
    
    # Get personalized recommendations
    personalized_recommendations = generate_personalized_recommendations(user, limit=12)
    
    # Get popular books
    popular_books = get_popular_books(limit=6)
    
    # Get user's reading stats
    reading_count = Issue.objects.filter(user=user).count()
    review_count = Review.objects.filter(user=user).count()
    
    # Get top genres user has interacted with
    top_genres = Genre.objects.filter(
        book__issues__user=user
    ).distinct()[:5]
    
    context = {
        'personalized_recommendations': personalized_recommendations,
        'popular_books': popular_books,
        'top_genres': top_genres,
        'reading_count': reading_count,
        'review_count': review_count,
    }
    return render(request, 'recommendation/recommendations.html', context)


@login_required
def recommendations_by_mood(request):
    """Get recommendations based on reading mood."""
    mood = request.GET.get('mood', 'happy')
    
    mood_choices = ['happy', 'sad', 'thriller', 'learn', 'relax']
    
    if mood not in mood_choices:
        mood = 'happy'
    
    recommendations = get_mood_based_recommendations(mood)
    
    context = {
        'mood': mood,
        'mood_choices': mood_choices,
        'recommendations': recommendations,
    }
    return render(request, 'recommendation/mood_recommendations.html', context)


@login_required
def genre_recommendations(request, genre_id):
    """Get recommendations for a specific genre."""
    try:
        genre = Genre.objects.get(id=genre_id)
    except Genre.DoesNotExist:
        return render(request, 'recommendation/genre_recommendations.html', {
            'error': 'Genre not found'
        })
    
    user = request.user
    
    # Get books from this genre that user hasn't read or wishlist'd
    from django.db.models import Count, Avg
    from apps.library.models import Book, Favorite
    
    borrowed_books = Issue.objects.filter(user=user).values_list('book_id', flat=True)
    favorite_books = Favorite.objects.filter(user=user).values_list('book_id', flat=True)
    
    books = Book.objects.filter(
        genre=genre
    ).exclude(
        id__in=borrowed_books
    ).exclude(
        id__in=favorite_books
    ).annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-review_count', '-avg_rating')
    
    context = {
        'genre': genre,
        'books': books,
        'recommendation_count': books.count(),
    }
    return render(request, 'recommendation/genre_recommendations.html', context)
