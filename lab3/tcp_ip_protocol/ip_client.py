import tcp_ip_protocol.router as router


class IpClient:
    def __init__(self, tcp_client, ip):
        self._ip = ip
        self._tcp_client = tcp_client

    @property
    def ip(self):
        return self._ip

    def get(self, ip_data):
        if self._ip != ip_data.receive_ip:
            raise Exception

        from_ip = ip_data.sender_ip
        tcp_data = ip_data.tcp_data
        self._tcp_client.get(tcp_data, from_ip)

    def send(self, to_ip, ip_data, is_wait=False):
        ip_data = self.create_ipdata(self._ip, to_ip, ip_data)
        router.send(ip_data, is_wait)

    @staticmethod
    def create_ipdata(from_ip, to_ip, tcp_data):
        return IPData(from_ip, to_ip, tcp_data)


class IPData:
    def __init__(self, from_ip, to_ip, tcp_data):
        self._data = {
            'version_number': 4,
            'header_len': 160,
            'service_type': 0,
            'packet_len': 1500,
            'fragment_id': 1,
            'df': 0,
            'mf': 0,
            'fragment_shift': 0,
            'life_time': 10,
            'protocol_type': 6,
            'control_sum': 12345,
            'sender_ip': from_ip,
            'receive_ip': to_ip,
            'tcp_data': tcp_data,
        }

    @property
    def sender_ip(self):
        return self._data['sender_ip']

    @property
    def receive_ip(self):
        return self._data['receive_ip']

    @property
    def tcp_data(self):
        return self._data['tcp_data']
