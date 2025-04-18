from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Country, City, VPNServer, User, VPNKey, TelegramBot
from .serializers import (
    CountrySerializer, CitySerializer, VPNServerSerializer,
    UserSerializer, VPNKeySerializer, TelegramBotSerializer,
    VPNServerRegistrationSerializer
)
from .utils.outline import OutlineVPNClient


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
            queryset = queryset.filter(country_id=country_id)
        return queryset


class VPNServerViewSet(viewsets.ModelViewSet):
    queryset = VPNServer.objects.all()
    serializer_class = VPNServerSerializer

    @action(detail=False, methods=['post'], serializer_class=VPNServerRegistrationSerializer)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def keys(self, request, pk=None):
        server = self.get_object()
        keys = VPNKey.objects.filter(vpn_server=server)
        serializer = VPNKeySerializer(keys, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        server = self.get_object()
        try:
            # Создаем клиент Outline для тестирования соединения
            client = OutlineVPNClient(api_url=server.api_url, cert_sha256=server.cert_sha)
            server_info = client.get_server_information()
            return Response({
                'status': 'success',
                'message': 'Connection successful',
                'server_info': server_info
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.all()
        telegram_id = self.request.query_params.get('telegram_id', None)
        if telegram_id is not None:
            queryset = queryset.filter(telegram_id=telegram_id)
        return queryset

    @action(detail=True, methods=['get'])
    def keys(self, request, pk=None):
        user = self.get_object()
        keys = VPNKey.objects.filter(user=user)
        serializer = VPNKeySerializer(keys, many=True)
        return Response(serializer.data)


class VPNKeyViewSet(viewsets.ModelViewSet):
    queryset = VPNKey.objects.all()
    serializer_class = VPNKeySerializer

    @action(detail=False, methods=['post'])
    def create_key(self, request):
        user_id = request.data.get('user_id')
        server_id = request.data.get('server_id')
        name = request.data.get('name', 'VPN Key')
        traffic_limit = request.data.get('traffic_limit', 0)  # в байтах
        expiration_days = request.data.get('expiration_days')

        user = get_object_or_404(User, id=user_id)
        server = get_object_or_404(VPNServer, id=server_id)

        try:
            # Создаем ключ VPN с помощью Outline API
            client = OutlineVPNClient(api_url=server.api_url, cert_sha256=server.cert_sha)

            # Создаем имя для ключа в Outline
            outline_key_name = f"{user.username or user.telegram_id} - {name}"

            # Создаем ключ в Outline
            key_data = client.create_key(name=outline_key_name)

            # Если указан лимит трафика, устанавливаем его
            if traffic_limit > 0:
                client.add_data_limit(key_data.key_id, traffic_limit)

            # Рассчитываем дату истечения срока действия, если указано количество дней
            expiration_date = None
            if expiration_days:
                from django.utils import timezone
                import datetime
                expiration_date = timezone.now() + datetime.timedelta(days=int(expiration_days))

            # Создаем запись о ключе в нашей базе данных
            vpn_key = VPNKey.objects.create(
                user=user,
                vpn_server=server,
                outline_id=key_data.key_id,
                access_url=key_data.access_url,
                name=name,
                expiration_date=expiration_date,
                traffic_limit=traffic_limit
            )

            serializer = VPNKeySerializer(vpn_key)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        vpn_key = self.get_object()
        server = vpn_key.vpn_server

        try:
            # Удаляем ключ через Outline API
            client = OutlineVPNClient(api_url=server.api_url, cert_sha256=server.cert_sha)
            client.delete_key(vpn_key.outline_id)

            # Обновляем статус ключа в нашей базе данных
            vpn_key.is_active = False
            vpn_key.save()

            return Response({'status': 'success', 'message': 'Key revoked successfully'})

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def update_traffic(self, request, pk=None):
        vpn_key = self.get_object()
        server = vpn_key.vpn_server

        try:
            # Получаем информацию о ключе через Outline API
            client = OutlineVPNClient(api_url=server.api_url, cert_sha256=server.cert_sha)
            key_info = client.get_key(vpn_key.outline_id)

            # Обновляем данные о трафике
            vpn_key.traffic_used = key_info.used_bytes
            vpn_key.save()

            serializer = VPNKeySerializer(vpn_key)
            return Response(serializer.data)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TelegramBotViewSet(viewsets.ModelViewSet):
    queryset = TelegramBot.objects.all()
    serializer_class = TelegramBotSerializer