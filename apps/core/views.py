from django.shortcuts import render
from apps.library.models import Book, Genre, Favorite, Issue, Review
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

# Create your views here.
def home(request):
    """Home page with featured content, popular books, and platform stats."""
    
    # Get featured books (first 6 by creation)
    featured_books = Book.objects.all()[:6]
    
    # Get recently added books
    recent_books = Book.objects.order_by('-created_at')[:8]
    
    # Get all genres
    genres = Genre.objects.all()[:10]
    
    # Get all books with their rating counts for "popular"
    popular_books = Book.objects.annotate(
        review_count=Count('reviews')
    ).order_by('-review_count')[:6]
    
    # Calculate platform stats
    total_books = Book.objects.count()
    total_users = Issue.objects.values('user').distinct().count()
    total_reviews = Review.objects.count()
    total_favorites = Favorite.objects.count()
    
    # Books borrowed this month
    month_start = timezone.now().replace(day=1)
    borrowed_this_month = Issue.objects.filter(issued_date__gte=month_start).count()
    
    context = {
        'featured_books': featured_books,
        'recent_books': recent_books,
        'popular_books': popular_books,
        'genres': genres,
        'total_books': total_books,
        'total_users': total_users,
        'total_reviews': total_reviews,
        'total_favorites': total_favorites,
        'borrowed_this_month': borrowed_this_month,
        'quotes': [
            {
                'text': 'A reader lives a thousand lives before he dies.',
                'author': 'George R.R. Martin'
            },
            {
                'text': 'Reading is to the mind what exercise is to the body.',
                'author': 'Joseph Addison'
            },
            {
                'text': 'The more that you read, the more things you will know.',
                'author': 'Dr. Seuss'
            },
            {
                'text': 'There is no friend as loyal as a book.',
                'author': 'Ernest Hemingway'
            },
            {
                'text': 'Books are a uniquely portable magic.',
                'author': 'Stephen King'
            },
        ]
    }
    return render(request, 'core/home.html', context)