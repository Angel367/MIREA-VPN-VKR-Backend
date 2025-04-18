from django.contrib import admin
from .models import Country, City, VPNServer, User, VPNKey, TelegramBot

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
    list_display = ('id', 'server_name', 'city', 'server_location', 'active', 'created_at')
    list_filter = ('active', 'city__country')
    search_fields = ('server_name', 'server_location')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_id', 'username', 'first_name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('telegram_id', 'username', 'first_name')
    readonly_fields = ('created_at', 'last_login')

@admin.register(VPNKey)
class VPNKeyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'vpn_server', 'created_at', 'expiration_date', 'is_active')
    list_filter = ('is_active', 'vpn_server')
    search_fields = ('name', 'user__username', 'user__telegram_id')
    readonly_fields = ('created_at', 'updated_at', 'outline_id', 'access_url')

@admin.register(TelegramBot)
class TelegramBotAdmin(admin.ModelAdmin):
    list_display = ('id', 'bot_username', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('bot_username',)
    readonly_fields = ('created_at', 'updated_at')