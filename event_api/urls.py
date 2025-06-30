from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from university_backend import settings
from .views import *

router = DefaultRouter()
router.register('', PostViewSet, basename='post')

urlpatterns = [
    path('event/', include(router.urls)),
    path('photos/', PhotoView.as_view(), name='photos'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)