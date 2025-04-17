from django.utils import timezone
from .models import User, VPNKey, VPNServer, Subscription
import logging
import subprocess
import os
import ipaddress
import random
import string
import requests

logger = logging.getLogger(__name__)


class VPNService:
    @staticmethod
    def get_free_servers():
        """Получить список доступных серверов"""
        return VPNServer.objects.filter(is_active=True)

    @staticmethod
    def generate_wireguard_key(user_id, server_id, subscription_id=None, duration=30):
        """Генерирует ключи WireGuard и сохраняет их в базе данных"""
        try:
            user = User.objects.get(id=user_id)
            server = VPNServer.objects.get(id=server_id)

            # Выбор подписки
            if subscription_id:
                subscription = Subscription.objects.get(id=subscription_id)
            else:
                subscription = Subscription.objects.get(name='free')

            # Генерация приватного и публичного ключей
            private_key = subprocess.check_output(["wg", "genkey"]).decode("utf-8").strip()
            public_key = subprocess.check_output(["wg", "pubkey"], input=private_key.encode()).decode("utf-8").strip()

            # Вычисление IP-адреса для клиента
            # Для простоты используем случайный IP из диапазона 10.0.0.0/24
            base_ip = "10.0.0."
            existing_ips = set(VPNKey.objects.filter(vpn_server=server).values_list('vpn_key', flat=True))

            # Найдем свободный IP
            client_ip = None
            for i in range(2, 254):
                test_ip = f"{base_ip}{i}"
                if test_ip not in existing_ips:
                    client_ip = test_ip
                    break

            if not client_ip:
                raise Exception("Нет доступных IP-адресов")

            # Создаем конфигурацию клиента
            client_config = f"""
            [Interface]
            PrivateKey = {private_key}
            Address = {client_ip}/24
            DNS = 8.8.8.8, 1.1.1.1

            [Peer]
            PublicKey = {server.api_key}
            AllowedIPs = 0.0.0.0/0
            Endpoint = {server.server_ip}:51820
            PersistentKeepalive = 25
            """

            # Рассчитываем дату истечения
            expiration_date = timezone.now() + timezone.timedelta(days=subscription.duration_days)

            # Создаем запись VPNKey
            vpn_key = VPNKey.objects.create(
                user=user,
                vpn_key=client_config,
                vpn_server=server,
                subscription=subscription,
                expiration_date=expiration_date,
                traffic_limit=subscription.traffic_limit_gb * 1024 * 1024 * 1024,  # Перевод из ГБ в байты
            )

            return vpn_key

        except Exception as e:
            logger.error(f"Ошибка при генерации ключа WireGuard: {str(e)}")
            raise

    @staticmethod
    def revoke_key(key_id):
        """Отзывает ключ VPN"""
        try:
            vpn_key = VPNKey.objects.get(id=key_id)
            # В реальной системе здесь бы отправлялся запрос к серверу VPN для удаления ключа
            vpn_key.delete()
            return True
        except VPNKey.DoesNotExist:
            logger.error(f"Ключ с ID {key_id} не найден")
            return False
        except Exception as e:
            logger.error(f"Ошибка при отзыве ключа: {str(e)}")
            return False

    @staticmethod
    def update_traffic_usage(key_id, bytes_used):
        """Обновляет информацию об использованном трафике"""
        try:
            vpn_key = VPNKey.objects.get(id=key_id)
            vpn_key.traffic_last_period_bytes += bytes_used

            # Проверяем, не превышен ли лимит трафика
            if vpn_key.traffic_last_period_bytes > vpn_key.traffic_limit:
                vpn_key.is_traffic_limit_exceeded = True

            vpn_key.save()
            return True
        except Exception as e:
            logger.error(f"Ошибка при обновлении информации о трафике: {str(e)}")
            return False

    @staticmethod
    def get_active_keys_for_user(user_id):
        """Получает список активных ключей пользователя"""
        now = timezone.now()
        return VPNKey.objects.filter(
            user_id=user_id,
            expiration_date__gt=now,
            is_traffic_limit_exceeded=False
        )

    @staticmethod
    def create_or_update_user(telegram_id, username=None, phone_number=None, first_name=None):
        """Создает или обновляет пользователя по Telegram ID"""
        user, created = User.objects.update_or_create(
            telegram_id=telegram_id,
            defaults={
                'username': username,
                'phone_number': phone_number,
                'first_name': first_name,
                'last_activity': timezone.now()
            }
        )
        return user