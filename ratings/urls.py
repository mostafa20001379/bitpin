from django.urls import path, include
from rest_framework_nested import routers

from .views import ContentViewSet, RatingViewSet

router = routers.DefaultRouter()
router.register(r'contents', ContentViewSet)

content_router = routers.NestedSimpleRouter(router, r'contents', lookup='content')
content_router.register(r'ratings', RatingViewSet, basename='content-ratings')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(content_router.urls)),
]
