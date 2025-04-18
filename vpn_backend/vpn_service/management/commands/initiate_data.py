from django.core.management.base import BaseCommand
from vpn_service.models import Country, City, TelegramBot, VPNServer
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Initialize database with required initial data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing data before initialization',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset = options.get('reset', False)

        if reset:
            self.stdout.write(self.style.WARNING('Resetting existing data...'))
            # Delete existing data in reverse order to avoid foreign key constraints
            VPNServer.objects.all().delete()
            City.objects.all().delete()
            Country.objects.all().delete()
            TelegramBot.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Data reset completed'))

        # Create countries
        self.stdout.write(self.style.NOTICE('Creating countries...'))
        countries = [
            {'country_name': 'United Kingdom'},
            {'country_name': 'United States'},
            {'country_name': 'Poland'},
            {'country_name': 'Sweden'},
            {'country_name': 'Russia'},
        ]

        country_objects = {}
        for country_data in countries:
            country, created = Country.objects.get_or_create(**country_data)
            country_objects[country.country_name] = country
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f"{status}: {country.country_name}")

        # Create cities
        self.stdout.write(self.style.NOTICE('Creating cities...'))
        cities = [
            {'city_name': 'Coventry', 'country': country_objects['United Kingdom']},
            {'city_name': 'Secaucus', 'country': country_objects['United States']},
            {'city_name': 'Warsaw', 'country': country_objects['Poland']},
            {'city_name': 'Stockholm', 'country': country_objects['Sweden']},
            {'city_name': 'Moscow', 'country': country_objects['Russia']},
        ]

        city_objects = {}
        for city_data in cities:
            city, created = City.objects.get_or_create(**city_data)
            city_objects[city.city_name] = city
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f"{status}: {city.city_name}, {city.country.country_name}")

        # Create default Telegram bot
        self.stdout.write(self.style.NOTICE('Creating default Telegram bot...'))
        default_bot_data = {
            'bot_id': '1',
            'bot_token': 'YOUR_BOT_TOKEN_HERE',  # This should be replaced with actual token
            'bot_username': 'vpn_access_bot',
            'is_active': True
        }

        bot, created = TelegramBot.objects.get_or_create(
            bot_id=default_bot_data['bot_id'],
            defaults=default_bot_data
        )

        status = 'Created' if created else 'Already exists'
        self.stdout.write(f"{status}: Telegram bot @{bot.bot_username}")

        # Register VPN servers based on predefined data
        self.stdout.write(self.style.NOTICE('Registering VPN servers...'))

        servers = [
            {
                'server_name': 'UK_Server',
                'city': city_objects['Coventry'],
                'server_location': 'Coventry, United Kingdom',
                'api_url': 'https://194.147.35.27:22422/server_api_url',
                'api_key': 'placeholder_api_key',
                'cert_sha': 'placeholder_cert_sha',
                'active': True
            },
            {
                'server_name': 'US_Server',
                'city': city_objects['Secaucus'],
                'server_location': 'Secaucus, United States',
                'api_url': 'https://77.105.162.202:22422/server_api_url',
                'api_key': 'placeholder_api_key',
                'cert_sha': 'placeholder_cert_sha',
                'active': True
            },
            {
                'server_name': 'Poland_Server',
                'city': city_objects['Warsaw'],
                'server_location': 'Warsaw, Poland',
                'api_url': 'https://192.145.28.82:22422/server_api_url',
                'api_key': 'placeholder_api_key',
                'cert_sha': 'placeholder_cert_sha',
                'active': True
            },
            {
                'server_name': 'Sweden_Server',
                'city': city_objects['Stockholm'],
                'server_location': 'Stockholm, Sweden',
                'api_url': 'https://192.145.30.254:22422/server_api_url',
                'api_key': 'placeholder_api_key',
                'cert_sha': 'placeholder_cert_sha',
                'active': True
            }
        ]

        for server_data in servers:
            server, created = VPNServer.objects.get_or_create(
                server_name=server_data['server_name'],
                defaults=server_data
            )

            status = 'Created' if created else 'Already exists'
            self.stdout.write(f"{status}: {server.server_name} ({server.server_location})")

        self.stdout.write(self.style.SUCCESS('Data initialization completed successfully!'))
        self.stdout.write(self.style.NOTICE(
            'Note: VPN server API URLs and credentials are placeholders. '
            'Replace them with actual values after Outline VPN installation.'
        ))