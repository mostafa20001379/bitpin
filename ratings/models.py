from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg, Count
from django.core.cache import cache
from datetime import timedelta
from django.utils import timezone


class Content(models.Model):
    title = text = models.CharField(max_length=200)
    text = models.TextField()
    cached_avg_rating = models.FloatField(default=0)
    cached_rating_count = models.IntegerField(default=0)
    last_cache_update = models.DateTimeField(auto_now=True)

    def update_cache(self):
        # Update cached values every 5 minutes
        if (timezone.now() - self.last_cache_update) > timedelta(minutes=5):
            ratings = Rating.objects.filter(content=self)
            self.cached_avg_rating = ratings.aggregate(Avg('score'))['score__avg'] or 0
            self.cached_rating_count = ratings.count()
            self.save()


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'content')
