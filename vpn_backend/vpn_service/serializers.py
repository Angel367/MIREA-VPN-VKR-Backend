from rest_framework import serializers
from vpn_service.models import Country, City, VPNServer, User, VPNKey, TelegramBot


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    country_name = serializers.ReadOnlyField(source='country.country_name')

    class Meta:
        model = City
        fields = ['id', 'city_name', 'country', 'country_name']


class VPNServerSerializer(serializers.ModelSerializer):
    city_name = serializers.ReadOnlyField(source='city.city_name')
    country_name = serializers.ReadOnlyField(source='city.country.country_name')

    class Meta:
        model = VPNServer
        fields = ['id', 'server_name', 'city', 'city_name', 'country_name',
                  'server_location', 'api_url', 'active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class VPNServerRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VPNServer
        fields = ['server_name', 'city', 'server_location', 'api_key', 'cert_sha', 'api_url']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'telegram_id', 'username', 'first_name', 'phone_number',
                  'created_at', 'last_login', 'is_active']
        read_only_fields = ['created_at', 'last_login']


class VPNKeySerializer(serializers.ModelSerializer):
    server_name = serializers.ReadOnlyField(source='vpn_server.server_name')
    server_location = serializers.ReadOnlyField(source='vpn_server.server_location')
    user_telegram_id = serializers.ReadOnlyField(source='user.telegram_id')

    class Meta:
        model = VPNKey
        fields = ['id', 'user', 'user_telegram_id', 'vpn_server', 'server_name',
                  'server_location', 'outline_id', 'access_url', 'name', 'created_at',
                  'updated_at', 'expiration_date', 'traffic_limit', 'traffic_used',
                  'traffic_last_period_bytes', 'is_active']
        read_only_fields = ['created_at', 'updated_at', 'outline_id', 'access_url']


class TelegramBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramBot
        fields = ['id', 'bot_id', 'bot_token', 'bot_username', 'created_at',
                  'updated_at', 'is_active']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'bot_token': {'write_only': True}
        }