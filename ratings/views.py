from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction
from django.core.cache import cache

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
    """ API endpoint that allows ratings to be viewed or edited. """
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

            # Spam protection logic
            self._process_rating_verification(rating)

        return Response(status=status.HTTP_201_CREATED)

    def _process_rating_verification(self, rating):
        # Get recent ratings count for this content
        recent_ratings_key = f'recent_ratings_{rating.content.id}'
        recent_ratings_count = cache.get(recent_ratings_key, 0)

        # If sudden spike in ratings, mark as unverified
        if recent_ratings_count > 100:  # Threshold for 5 minutes
            rating.is_verified = False
        else:
            rating.is_verified = True

        rating.save()

        # Increment recent ratings counter
        cache.incr(recent_ratings_key, 1)
        cache.expire(recent_ratings_key, 300)  # 5 minutes expiry
