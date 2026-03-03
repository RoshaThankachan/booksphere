import os
from django.db.models import Count, Avg, Q
from apps.library.models import Book, Genre, Issue, Review, Favorite
from .models import Recommendation

def get_popular_books(limit=6):
    """Get most popular books based on reviews and ratings."""
    return Book.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).filter(
        reviews__isnull=False
    ).order_by('-review_count', '-avg_rating')[:limit]


def get_genre_based_recommendations(user, limit=6):
    """Recommend books from genres user has shown interest in."""
    # Get genres from user's borrowed books
    borrowed_genres = Genre.objects.filter(
        book__issues__user=user
    ).annotate(
        borrow_count=Count('book__issues', filter=Q(book__issues__user=user))
    ).order_by('-borrow_count')[:3]
    
    if not borrowed_genres:
        # Fallback: Get genres from wishlist
        borrowed_genres = Genre.objects.filter(
            book__favorite__user=user
        ).annotate(
            favorite_count=Count('book__favorite', filter=Q(book__favorite__user=user))
        ).order_by('-favorite_count')[:3]
    
    if not borrowed_genres:
        # Fallback: Return top-rated books from all genres
        return Book.objects.annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).filter(reviews__isnull=False).order_by('-avg_rating')[:limit]
    
    # Get books from these genres (excluding already borrowed/favorited)
    borrowed_books = Issue.objects.filter(user=user).values_list('book_id', flat=True)
    favorite_books = Favorite.objects.filter(user=user).values_list('book_id', flat=True)
    excluded_books = set(list(borrowed_books) + list(favorite_books))
    
    recommendations = Book.objects.filter(
        genre__in=borrowed_genres
    ).exclude(
        id__in=excluded_books
    ).annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-review_count', '-avg_rating')[:limit]
    
    return recommendations


def get_reading_history_recommendations(user, limit=6):
    """Recommend books similar to ones user has read based on genre and author."""
    # Get books user has borrowed
    borrowed_books = Issue.objects.filter(user=user).select_related('book')
    
    if not borrowed_books.exists():
        return []
    
    # Get genres and authors from borrowed books
    authors = set()
    genres = set()
    for issue in borrowed_books[:5]:  # Last 5 borrowed books
        authors.add(issue.book.author_id)
        genres.add(issue.book.genre_id)
    
    # Find books by same authors or in same genres (excluding borrowed)
    borrowed_book_ids = Issue.objects.filter(user=user).values_list('book_id', flat=True)
    
    similar_books = Book.objects.filter(
        Q(author_id__in=authors) | Q(genre_id__in=genres)
    ).exclude(
        id__in=borrowed_book_ids
    ).exclude(
        id__in=Favorite.objects.filter(user=user).values_list('book_id', flat=True)
    ).annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-review_count', '-avg_rating')[:limit]
    
    return similar_books


def get_highly_rated_by_category(user, limit=6):
    """Get highly-rated books in genres user has rated positively."""
    # Get genres where user gave high ratings
    high_rated_reviews = Review.objects.filter(
        user=user,
        rating__gte=4
    ).select_related('book__genre').values('book__genre_id').annotate(
        count=Count('id')
    ).order_by('-count')[:3]
    
    if not high_rated_reviews:
        return []
    
    genre_ids = [r['book__genre_id'] for r in high_rated_reviews]
    borrowed_books = Issue.objects.filter(user=user).values_list('book_id', flat=True)
    
    recommendations = Book.objects.filter(
        genre_id__in=genre_ids,
        reviews__rating__gte=4
    ).exclude(
        id__in=borrowed_books
    ).exclude(
        id__in=Favorite.objects.filter(user=user).values_list('book_id', flat=True)
    ).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).filter(
        review_count__gte=2
    ).order_by('-avg_rating', '-review_count')[:limit]
    
    return recommendations


def generate_personalized_recommendations(user, limit=12):
    """
    Generate comprehensive personalized recommendations for user.
    Combines multiple recommendation strategies.
    """
    recommendations = []
    
    # 1. Genre-based (40% weight)
    genre_recs = get_genre_based_recommendations(user, limit=5)
    for book in genre_recs:
        recommendations.append({
            'book': book,
            'reason': 'genre_match',
            'score': 75
        })
    
    # 2. Reading history similar books (30% weight)
    history_recs = get_reading_history_recommendations(user, limit=4)
    for book in history_recs:
        recommendations.append({
            'book': book,
            'reason': 'similar_to_read',
            'score': 65
        })
    
    # 3. Highly rated in user's preferred genres (20% weight)
    rated_recs = get_highly_rated_by_category(user, limit=3)
    for book in rated_recs:
        recommendations.append({
            'book': book,
            'reason': 'highly_rated',
            'score': 80
        })
    
    # 4. Popular books (10% weight)
    if len(recommendations) < limit:
        popular_recs = get_popular_books(limit=3)
        for book in popular_recs:
            # Check if not already recommended
            if not any(r['book'].id == book.id for r in recommendations):
                recommendations.append({
                    'book': book,
                    'reason': 'popular',
                    'score': 60
                })
    
    # Remove duplicates and return unique recommendations
    seen_ids = set()
    unique_recs = []
    for rec in recommendations:
        if rec['book'].id not in seen_ids:
            seen_ids.add(rec['book'].id)
            unique_recs.append(rec)
    
    return unique_recs[:limit]


def get_mood_based_recommendations(mood):
    """
    Placeholder for mood-based suggestions.
    Can be enhanced with mapping moods to genres.
    """
    mood_genre_map = {
        'happy': ['Fiction', 'Comedy', 'Romance'],
        'sad': ['Drama', 'Literary Fiction'],
        'thriller': ['Mystery', 'Crime', 'Thriller'],
        'learn': ['Non-Fiction', 'Self-Help', 'Science'],
        'relax': ['Poetry', 'Fiction', 'Fantasy'],
    }
    
    genres = mood_genre_map.get(mood, [])
    if genres:
        return Book.objects.filter(
            genre__name__in=genres
        ).annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating')[:6]
    
    return []

