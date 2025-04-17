from django.core.management.base import BaseCommand
from vpn.models import Country, City, VPNServer, Subscription


class Command(BaseCommand):
    help = 'Initialize database with basic data'

    def handle(self, *args, **kwargs):
        # Создаем страны
        uk = Country.objects.create(country_name="United Kingdom")
        usa = Country.objects.create(country_name="United States")
        poland = Country.objects.create(country_name="Poland")
        sweden = Country.objects.create(country_name="Sweden")
        russia = Country.objects.create(country_name="Russia")

        # Создаем города
        moscow = City.objects.create(city_name="Moscow", country=russia)
        coventry = City.objects.create(city_name="Coventry", country=uk)
        secaucus = City.objects.create(city_name="Secaucus", country=usa)
        warsaw = City.objects.create(city_name="Warsaw", country=poland)
        stockholm = City.objects.create(city_name="Stockholm", country=sweden)

        # Создаем сервера
        VPNServer.objects.create(
            server_name="Moscow VPN",
            server_ip="194.87.252.26",
            server_location=moscow,
            api_key="generated_api_key_1"
        )

        VPNServer.objects.create(
            server_name="Coventry VPN",
            server_ip="194.147.35.27",
            server_location=coventry,
            api_key="generated_api_key_2"
        )

        VPNServer.objects.create(
            server_name="Secaucus VPN",
            server_ip="77.105.162.202",
            server_location=secaucus,
            api_key="generated_api_key_3"
        )

        VPNServer.objects.create(
            server_name="Warsaw VPN",
            server_ip="192.145.28.82",
            server_location=warsaw,
            api_key="generated_api_key_4"
        )

        VPNServer.objects.create(
            server_name="Stockholm VPN",
            server_ip="192.145.30.254",
            server_location=stockholm,
            api_key="generated_api_key_5"
        )

        # Создаем тарифные планы
        Subscription.objects.create(
            name="free",
            price=0.00,
            duration_days=3,
            traffic_limit_gb=1,
            max_devices=1
        )

        Subscription.objects.create(
            name="basic",
            price=5.99,
            duration_days=30,
            traffic_limit_gb=50,
            max_devices=2
        )

        Subscription.objects.create(
            name="premium",
            price=9.99,
            duration_days=30,
            traffic_limit_gb=100,
            max_devices=5
        )

        self.stdout.write(self.style.SUCCESS('Successfully initialized data'))