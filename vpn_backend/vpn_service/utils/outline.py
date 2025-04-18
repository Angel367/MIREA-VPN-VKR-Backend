from outline_vpn.outline_vpn import OutlineVPN


class OutlineVPNClient:
    def __init__(self, api_url, cert_sha256=None):
        self.client = OutlineVPN(api_url=api_url, cert_sha256=cert_sha256)

    def get_keys(self):
        return self.client.get_keys()

    def get_key(self, key_id):
        return self.client.get_key(key_id)

    def create_key(self, name=None):
        return self.client.create_key(name=name)

    def delete_key(self, key_id):
        return self.client.delete_key(key_id)

    def rename_key(self, key_id, name):
        return self.client.rename_key(key_id, name)

    def add_data_limit(self, key_id, limit_bytes):
        return self.client.add_data_limit(key_id, limit_bytes)

    def delete_data_limit(self, key_id):
        return self.client.delete_data_limit(key_id)

    def get_server_information(self):
        return self.client.get_server_information()

    def get_server_stats(self):
        try:
            metrics = self.client.get_metrics()
            return {
                'transferred_bytes': metrics.transferred_bytes,
                'connected_clients': len(metrics.connected_clients)
            }
        except:
            return {
                'transferred_bytes': 0,
                'connected_clients': 0
            }

    def gb_to_bytes(self, gb):
        """Преобразует гигабайты в байты"""
        bytes_in_gb = 1024 ** 3  # 1 ГБ = 1024^3 байт
        return int(gb * bytes_in_gb)