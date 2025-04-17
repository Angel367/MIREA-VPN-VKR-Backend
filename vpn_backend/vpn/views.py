from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Country, City, VPNServer, VPNService, TelegramBot, User, VPNKey, Subscription
from .serializers import (
    CountrySerializer, CitySerializer, VPNServerSerializer,
    VPNServiceSerializer, TelegramBotSerializer, UserSerializer,
    VPNKeySerializer, SubscriptionSerializer, VPNConfigSerializer
)
from .services import VPNService as VPNServiceLogic


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def get_queryset(self):
        queryset = City.objects.all()
        country_id = self.request.query_params.get('country_id', None)
        if country_id is not None:
            queryset = queryset.filter(country__id=country_id)
        return queryset


class VPNServerViewSet(viewsets.ModelViewSet):
    queryset = VPNServer.objects.all()
    serializer_class = VPNServerSerializer

    def get_queryset(self):
        queryset = VPNServer.objects.all()
        city_id = self.request.query_params.get('city_id', None)
        if city_id is not None:
            queryset = queryset.filter(server_location__id=city_id)
        return queryset

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        server = self.get_object()
        server.is_active = not server.is_active
        server.save()
        return Response({'status': 'server status updated', 'is_active': server.is_active})


class VPNServiceViewSet(viewsets.ModelViewSet):
    queryset = VPNService.objects.all()
    serializer_class = VPNServiceSerializer

    def get_queryset(self):
        queryset = VPNService.objects.all()
        server_id = self.request.query_params.get('server_id', None)
        if server_id is not None:
            queryset = queryset.filter(server__id=server_id)
        return queryset


class TelegramBotViewSet(viewsets.ModelViewSet):
    queryset = TelegramBot.objects.all()
    serializer_class = TelegramBotSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'])
    def by_telegram_id(self, request):
        telegram_id = request.query_params.get('telegram_id', None)
        if telegram_id is not None:
            user = get_object_or_404(User, telegram_id=telegram_id)
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        return Response(
            {"error": "telegram_id parameter is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['get'])
    def active_keys(self, request, pk=None):
        keys = VPNServiceLogic.get_active_keys_for_user(pk)
        serializer = VPNKeySerializer(keys, many=True)
        return Response(serializer.data)


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer


class VPNKeyViewSet(viewsets.ModelViewSet):
    queryset = VPNKey.objects.all()
    serializer_class = VPNKeySerializer

    @action(detail=False, methods=['post'])
    def generate_key(self, request):
        user_id = request.data.get('user_id')
        server_id = request.data.get('server_id')
        subscription_id = request.data.get('subscription_id')

        if not user_id or not server_id:
            return Response(
                {"error": "user_id and server_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            vpn_key = VPNServiceLogic.generate_wireguard_key(
                user_id,
                server_id,
                subscription_id
            )
            serializer = VPNKeySerializer(vpn_key)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        success = VPNServiceLogic.revoke_key(pk)
        if success:
            return Response({"status": "key revoked successfully"})
        return Response(
            {"error": "Failed to revoke key"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @action(detail=True, methods=['post'])
    def update_traffic(self, request, pk=None):
        bytes_used = request.data.get('bytes_used', 0)
        success = VPNServiceLogic.update_traffic_usage(pk, bytes_used)
        if success:
            return Response({"status": "traffic updated successfully"})
        return Response(
            {"error": "Failed to update traffic"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @action(detail=True, methods=['get'])
    def get_config(self, request, pk=None):
        vpn_key = self.get_object()

        # Проверяем срок действия и лимит трафика
        if vpn_key.is_expired():
            return Response(
                {"error": "VPN key has expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if vpn_key.is_traffic_limit_exceeded:
            return Response(
                {"error": "Traffic limit exceeded"},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = {
            'config': vpn_key.vpn_key,
            'server_name': vpn_key.vpn_server.server_name,
            'server_location': str(vpn_key.vpn_server.server_location),
            'expiration_date': vpn_key.expiration_date,
            'traffic_limit': vpn_key.traffic_limit
        }

        serializer = VPNConfigSerializer(data)
        return Response(serializer.data)