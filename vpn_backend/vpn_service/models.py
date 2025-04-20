from django.db import models
from django.utils import timezone



class Country(models.Model):
    id = models.AutoField(primary_key=True)
    country_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.country_name


class City(models.Model):
    id = models.AutoField(primary_key=True)
    city_name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')

    class Meta:
        unique_together = ('city_name', 'country')

    def __str__(self):
        return f"{self.city_name}, {self.country.country_name}"


class VPNServer(models.Model):
    id = models.AutoField(primary_key=True)
    server_name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='servers')
    server_location = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)
    cert_sha = models.CharField(max_length=255)
    api_url = models.URLField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.server_name} - {self.city}"


class User(models.Model):
    id = models.AutoField(primary_key=True)
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username or self.telegram_id}"


class VPNKey(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vpn_keys')
    vpn_server = models.ForeignKey(VPNServer, on_delete=models.CASCADE, related_name='vpn_keys')
    outline_id = models.CharField(max_length=50)
    access_url = models.CharField(max_length=255)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    traffic_limit = models.BigIntegerField(default=0)  # в байтах
    traffic_last_period_bytes = models.BigIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    @property
    def traffic_used(self):
        from .utils.outline import OutlineVPNClient
        client = OutlineVPNClient(api_url=self.vpn_server.api_url, cert_sha256=self.vpn_server.cert_sha)
        if client.get_key(key_id=self.outline_id).used_bytes is not None:
            return client.get_key(key_id=self.outline_id).used_bytes
        else:
            return 0

    def __str__(self):
        return f"{self.name} - {self.user}"

    def is_expired(self):
        if self.expiration_date:
            return timezone.now() > self.expiration_date
        return False

    def traffic_limit_exceeded(self):
        if self.traffic_limit > 0:
            return self.traffic_used >= self.traffic_limit
        return False


class TelegramBot(models.Model):
    id = models.AutoField(primary_key=True)
    bot_id = models.CharField(max_length=50, unique=True)
    bot_token = models.CharField(max_length=100)
    bot_username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.bot_username
