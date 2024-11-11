from rest_framework import serializers

from .models import Content, Rating


class ContentListSerializer(serializers.ModelSerializer):
    avg_rating = serializers.FloatField(source='cached_avg_rating')
    rating_count = serializers.IntegerField(source='cached_rating_count')
    user_rating = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = ['id', 'title', 'avg_rating', 'rating_count', 'user_rating']

    def get_user_rating(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            rating = Rating.objects.filter(user=user, content=obj).first()
            return rating.score if rating else None
        return None


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['score']
