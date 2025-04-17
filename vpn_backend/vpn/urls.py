from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CountryViewSet, CityViewSet, VPNServerViewSet,
    VPNServiceViewSet, TelegramBotViewSet, UserViewSet,
    VPNKeyViewSet, SubscriptionViewSet
)

router = DefaultRouter()
router.register(r'countries', CountryViewSet)
router.register(r'cities', CityViewSet)
router.register(r'servers', VPNServerViewSet)
router.register(r'services', VPNServiceViewSet)
router.register(r'bots', TelegramBotViewSet)
router.register(r'users', UserViewSet)
router.register(r'keys', VPNKeyViewSet)
router.register(r'subscriptions', SubscriptionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]