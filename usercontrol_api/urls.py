from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from .views import *

group_router = DefaultRouter()
group_router.register('', GroupViewSet, basename='group')

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    path('register/', RegisterView.as_view(), name='register'),
    path('me/', MeView.as_view(), name='me'),
    path('group/', include(group_router.urls)),
]