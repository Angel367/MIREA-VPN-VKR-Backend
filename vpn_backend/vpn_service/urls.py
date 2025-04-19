from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CountryViewSet, CityViewSet, VPNServerViewSet,
    UserViewSet, VPNKeyViewSet, TelegramBotViewSet
)

router = DefaultRouter()
router.register(r'countries', CountryViewSet)
router.register(r'cities', CityViewSet)
router.register(r'servers', VPNServerViewSet)
router.register(r'users', UserViewSet)
router.register(r'keys', VPNKeyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]