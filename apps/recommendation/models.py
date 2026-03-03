from django.db import models
from django.contrib.auth.models import User
from apps.library.models import Book

class UserPreference(models.Model):
    """Track user preferences and reading patterns for better recommendations."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preference')
    favorite_genres = models.JSONField(default=list, blank=True)  # List of genre IDs
    reading_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='intermediate'
    )
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"


class Recommendation(models.Model):
    """Store personalized recommendations for each user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    reason = models.CharField(
        max_length=100,
        choices=[
            ('popular', 'Popular Book'),
            ('genre_match', 'Matches Your Interests'),
            ('similar_to_read', 'Similar to Books You Read'),
            ('highly_rated', 'Highly Rated in Your Genre'),
            ('trending', 'Currently Trending'),
        ]
    )
    score = models.FloatField(default=0.0)  # Recommendation strength (0-100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score', '-created_at']
        unique_together = ('user', 'book', 'reason')

    def __str__(self):
        return f"Recommend {self.book.title} to {self.user.username}"
