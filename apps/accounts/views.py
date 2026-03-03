

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import SignupForm, LoginForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from .models import Profile
from apps.library.models import Issue, Favorite, Review
from django.db.models import Count, Q


# 🔹 Signup View
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


# 🔹 Login View
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


# 🔹 Logout View
def logout_view(request):
    logout(request)
    return redirect('home')


# 🔹 Dashboard View
@login_required
def dashboard(request):
    """Main dashboard displaying user profile, stats, and quick actions."""
    user = request.user
    profile = user.profile
    
    # Get user statistics
    favorites_count = Favorite.objects.filter(user=user).count()
    borrowed_count = Issue.objects.filter(user=user, is_returned=False).count()
    returned_count = Issue.objects.filter(user=user, is_returned=True).count()
    reviews_count = Review.objects.filter(user=user).count()
    
    # Get recent activities
    recent_favorites = Favorite.objects.filter(user=user).select_related('book')[:5]
    recent_borrowed = Issue.objects.filter(user=user).select_related('book').order_by('-issued_date')[:5]
    
    context = {
        'profile': profile,
        'favorites_count': favorites_count,
        'borrowed_count': borrowed_count,
        'returned_count': returned_count,
        'reviews_count': reviews_count,
        'recent_favorites': recent_favorites,
        'recent_borrowed': recent_borrowed,
    }
    return render(request, 'accounts/dashboard.html', context)


# 🔹 Profile Detail View
@login_required
def profile_detail(request):
    """Display user profile details."""
    user = request.user
    profile = user.profile
    
    # Get user statistics
    favorites_count = Favorite.objects.filter(user=user).count()
    borrowed_count = Issue.objects.filter(user=user).count()
    reviews_count = Review.objects.filter(user=user).count()
    
    context = {
        'profile': profile,
        'user': user,
        'favorites_count': favorites_count,
        'borrowed_count': borrowed_count,
        'reviews_count': reviews_count,
    }
    return render(request, 'accounts/profile_detail.html', context)


# 🔹 Profile Update View
@login_required
def profile_update(request):
    """Update user profile and user information."""
    user = request.user
    profile = user.profile
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile, user=user)
        if form.is_valid():
            form.save()
            return redirect('profile_detail')
    else:
        form = ProfileUpdateForm(instance=profile, user=user)
    
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'accounts/profile_update.html', context)


# 🔹 Download History View
@login_required
def download_history(request):
    """Display user's book download/borrow history."""
    user = request.user
    
    # Get all borrowed books
    borrowed_history = Issue.objects.filter(user=user).select_related('book').order_by('-issued_date')
    
    # Separate active and returned
    active_borrows = borrowed_history.filter(is_returned=False)
    returned_borrows = borrowed_history.filter(is_returned=True)
    
    context = {
        'active_borrows': active_borrows,
        'returned_borrows': returned_borrows,
        'total_borrowed': borrowed_history.count(),
    }
    return render(request, 'accounts/download_history.html', context)


# 🔹 User Reviews View
@login_required
def user_reviews(request):
    """Display all reviews written by the user."""
    user = request.user
    reviews = Review.objects.filter(user=user).select_related('book').order_by('-created_at')
    
    context = {
        'reviews': reviews,
        'total_reviews': reviews.count(),
    }
    return render(request, 'accounts/user_reviews.html', context)
