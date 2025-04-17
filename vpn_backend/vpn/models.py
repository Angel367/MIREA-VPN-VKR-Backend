from django.db import models
from django.utils import timezone
import uuid


class Country(models.Model):
    id = models.AutoField(primary_key=True)
    country_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.country_name


class City(models.Model):
    id = models.AutoField(primary_key=True)
    city_name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return f"{self.city_name}, {self.country.country_name}"

    class Meta:
        unique_together = ['city_name', 'country']


class VPNServer(models.Model):
    id = models.AutoField(primary_key=True)
    server_name = models.CharField(max_length=100, unique=True)
    server_ip = models.GenericIPAddressField(unique=True)
    server_location = models.ForeignKey(City, on_delete=models.CASCADE, related_name='vpn_servers')
    api_key = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.server_name


class VPNService(models.Model):
    id = models.AutoField(primary_key=True)
    server = models.ForeignKey(VPNServer, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    protocol = models.CharField(max_length=50, choices=[
        ('wireguard', 'WireGuard'),
        ('openvpn', 'OpenVPN'),
        ('ikev2', 'IKEv2'),
    ], default='wireguard')
    port = models.IntegerField(default=51820)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.protocol}) on {self.server.server_name}"

    class Meta:
        unique_together = ['server', 'protocol', 'port']


class TelegramBot(models.Model):
    id = models.AutoField(primary_key=True)
    bot_token = models.CharField(max_length=255, unique=True)
    service = models.ForeignKey(VPNService, on_delete=models.CASCADE, related_name='bots')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Bot for {self.service.name}"


class User(models.Model):
    id = models.AutoField(primary_key=True)
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username or f"User {self.telegram_id}"


class Subscription(models.Model):
    SUBSCRIPTION_TYPES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, choices=SUBSCRIPTION_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()
    traffic_limit_gb = models.IntegerField()
    max_devices = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.name} - {self.duration_days} days"


class VPNKey(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vpn_keys')
    vpn_key = models.TextField()
    vpn_server = models.ForeignKey(VPNServer, on_delete=models.CASCADE, related_name='vpn_keys')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, related_name='vpn_keys')
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField()
    traffic_last_period_bytes = models.BigIntegerField(default=0)
    traffic_limit = models.BigIntegerField(default=0)  # в байтах
    is_traffic_limit_exceeded = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.expiration_date

    def update_expiration_date(self, days):
        if self.is_expired():
            self.expiration_date = timezone.now() + timezone.timedelta(days=days)
        else:
            self.expiration_date = self.expiration_date + timezone.timedelta(days=days)
        self.save()

    def revoke_key(self):
        # Логика отзыва ключа будет реализована в сервисе
        pass

    def __str__(self):
        return f"VPN Key for {self.user} on {self.vpn_server.server_name} (expires: {self.expiration_date})"