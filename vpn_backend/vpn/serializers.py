from rest_framework import serializers
from .models import Country, City, VPNServer, VPNService, TelegramBot, User, VPNKey, Subscription


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'country_name']


class CitySerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.country_name', read_only=True)

    class Meta:
        model = City
        fields = ['id', 'city_name', 'country', 'country_name']


class VPNServerSerializer(serializers.ModelSerializer):
    server_location_name = serializers.CharField(source='server_location.__str__', read_only=True)

    class Meta:
        model = VPNServer
        fields = ['id', 'server_name', 'server_ip', 'server_location', 'server_location_name', 'is_active']
        extra_kwargs = {
            'api_key': {'write_only': True}
        }


class VPNServiceSerializer(serializers.ModelSerializer):
    server_name = serializers.CharField(source='server.server_name', read_only=True)

    class Meta:
        model = VPNService
        fields = ['id', 'server', 'server_name', 'name', 'protocol', 'port', 'created_at']


class TelegramBotSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.__str__', read_only=True)

    class Meta:
        model = TelegramBot
        fields = ['id', 'bot_token', 'service', 'service_name', 'is_active']
        extra_kwargs = {
            'bot_token': {'write_only': True}
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'telegram_id', 'username', 'phone_number', 'first_name', 'created_at', 'last_activity',
                  'is_active']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'name', 'price', 'duration_days', 'traffic_limit_gb', 'max_devices']


class VPNKeySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    server_name = serializers.CharField(source='vpn_server.server_name', read_only=True)
    subscription_name = serializers.CharField(source='subscription.name', read_only=True)

    class Meta:
        model = VPNKey
        fields = [
            'id', 'user', 'username', 'vpn_key', 'vpn_server', 'server_name',
            'subscription', 'subscription_name', 'created_at', 'expiration_date',
            'traffic_last_period_bytes', 'traffic_limit', 'is_traffic_limit_exceeded'
        ]
        extra_kwargs = {
            'vpn_key': {'write_only': True}
        }


class VPNConfigSerializer(serializers.Serializer):
    config = serializers.CharField()
    server_name = serializers.CharField()
    server_location = serializers.CharField()
    expiration_date = serializers.DateTimeField()
    traffic_limit = serializers.IntegerField()