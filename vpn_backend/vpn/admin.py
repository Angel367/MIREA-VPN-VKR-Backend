from django.contrib import admin
from .models import Country, City, VPNServer, VPNService, TelegramBot, User, VPNKey, Subscription

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'country_name')
    search_fields = ('country_name',)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'city_name', 'country')
    list_filter = ('country',)
    search_fields = ('city_name',)

@admin.register(VPNServer)
class VPNServerAdmin(admin.ModelAdmin):
    list_display = ('id', 'server_name', 'server_ip', 'server_location', 'is_active')
    list_filter = ('is_active', 'server_location__country')
    search_fields = ('server_name', 'server_ip')

@admin.register(VPNService)
class VPNServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'server', 'protocol', 'port', 'created_at')
    list_filter = ('protocol', 'server')
    search_fields = ('name',)

@admin.register(TelegramBot)
class TelegramBotAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'is_active')
    list_filter = ('is_active', 'service')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_id', 'username', 'first_name', 'last_activity', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('username', 'telegram_id', 'first_name')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'duration_days', 'traffic_limit_gb', 'max_devices')
    list_filter = ('name',)
    search_fields = ('name',)

@admin.register(VPNKey)
class VPNKeyAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'vpn_server', 'created_at', 'expiration_date', 'is_traffic_limit_exceeded')
    list_filter = ('vpn_server', 'is_traffic_limit_exceeded')
    search_fields = ('user__username', 'user__telegram_id')
    readonly_fields = ('traffic_last_period_bytes',)
    date_hierarchy = 'created_at'