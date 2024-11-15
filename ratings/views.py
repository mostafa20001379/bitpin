from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction
from django.core.cache import cache
from datetime import datetime, timedelta

from .models import Content, Rating
from .serializers import ContentListSerializer, RatingSerializer


class ContentViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows content to be viewed or edited. """
    queryset = Content.objects.all()
    serializer_class = ContentListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        for content in queryset:
            content.update_cache()
        return queryset


class RatingViewSet(viewsets.ModelViewSet):
    """API endpoint that allows ratings to be viewed or edited."""
    serializer_class = RatingSerializer

    def create(self, request, *args, **kwargs):
        content_id = kwargs.get('content_pk')
        user = request.user
        score = request.data.get('score')

        with transaction.atomic():
            rating, created = Rating.objects.get_or_create(
                user=user,
                content_id=content_id,
                defaults={'score': score}
            )

            if not created:
                rating.score = score
                rating.save()

            # Advanced spam detection logic
            self._process_rating_verification(rating)

        return Response(status=status.HTTP_201_CREATED)

    def _process_rating_verification(self, rating):
        content = rating.content

        # Get recent ratings for this content
        recent_ratings = Rating.objects.filter(
            content=content,
            created_at__gte=datetime.now() - timedelta(minutes=5)
        )
        recent_ratings_count = recent_ratings.count()

        # Detect rating patterns
        low_ratings_count = recent_ratings.filter(score__lte=1).count()
        high_ratings_count = recent_ratings.filter(score__gte=4).count()

        # Define thresholds for spam detection
        spike_threshold = 100  # Sudden spike in ratings
        low_rating_ratio_threshold = 0.6  # >60% low ratings in a short period
        high_rating_ratio_threshold = 0.6  # >60% high ratings in a short period

        # Mark as unverified if suspicious patterns are detected
        if (
            recent_ratings_count > spike_threshold or
            (low_ratings_count / recent_ratings_count) > low_rating_ratio_threshold or
            (high_ratings_count / recent_ratings_count) > high_rating_ratio_threshold
        ):
            rating.is_verified = False
        else:
            rating.is_verified = True

        # Save the rating verification status
        rating.save()

        # Increment the recent ratings counter in the cache
        recent_ratings_key = f'recent_ratings_{content.id}'
        if not cache.get(recent_ratings_key):
            cache.set(recent_ratings_key, 0)
        cache.incr(recent_ratings_key, 1)
        cache.expire(recent_ratings_key, 300)  # Cache expiry: 5 minutes

