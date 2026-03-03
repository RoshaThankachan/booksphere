from django.shortcuts import render, get_object_or_404, redirect
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required

# Create your views here.
from .models import Book, Favorite

from django.db.models import Q

from .models import Genre

from django.core.paginator import Paginator

def book_list(request):
    """Display searchable/paginated list of books.

    If the user is authenticated we also fetch the set of their favorite
    book IDs so the template can render the heart symbol accordingly.
    """

    query = request.GET.get('q')
    genre_id = request.GET.get('genre')

    books = Book.objects.all()

    if query:
        books = books.filter(title__icontains=query)

    if genre_id:
        books = books.filter(genre_id=genre_id)

    paginator = Paginator(books, 6)  # 6 books per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    favorite_ids = set()
    if request.user.is_authenticated:
        favorite_ids = set(
            Favorite.objects.filter(user=request.user).values_list('book_id', flat=True)
        )

    context = {
        'page_obj': page_obj,
        'genres': Genre.objects.all(),
        'selected_genre_id': int(genre_id) if genre_id else None,
        'favorite_ids': favorite_ids,
    }
    return render(request, 'library/book_list.html', context)








def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    reviews = book.reviews.all()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
    else:
        form = ReviewForm()

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, book=book).exists()

    return render(request, 'library/book_detail.html', {
        'book': book,
        'form': form,
        'reviews': reviews,
        'is_favorite': is_favorite,
    })


from django.db.models import Avg

def average_rating(self):
    return self.review_set.aggregate(Avg('rating'))['rating__avg'] or 0


@login_required
def toggle_favorite(request, pk):
    """Add or remove a book from the logged-in user's favorites.

    This view is intentionally simple: clicking the heart icon performs a GET
    request that toggles the existence of a Favorite record and then redirects
    back to the referring page.  The decorator enforces login.
    """
    book = get_object_or_404(Book, pk=pk)
    fav, created = Favorite.objects.get_or_create(user=request.user, book=book)
    if not created:
        fav.delete()

    # send back to where the user was; fall back to list view
    return redirect(request.META.get('HTTP_REFERER', 'book_list'))


@login_required
def favorites_list(request):
    """Render a page showing all of the user's favorite books."""
    user_favorites = Favorite.objects.filter(user=request.user).select_related('book')
    return render(request, 'library/favorites.html', {'favorites': user_favorites})
