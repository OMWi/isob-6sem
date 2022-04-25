from tcp_ip_protocol.tcp_client import TcpClient

class Client:
    def __init__(self, ip, ports, is_server=False):
        self._ip = ip
        self._ports = ports
        self._tcp_client = TcpClient(self, ip, ports)
        self._type = 'Server' if is_server else 'Client'

    @property
    def ip(self):
        return self._ip
    @property
    def ports(self):
        return self._ports
    @property
    def tcp_client(self):
        return self._tcp_client
        
    def __str__(self):
        return f'{self._type} {self._ip}:{{port}}'
    def to_str(self, port=None):
        if not port:
            port = self._ports[0]
        return str(self).format(port=port)

    def connect(self, to_ip, to_port, from_port=None):
        if not from_port:
            from_port = self._ports[0]

        result = self._tcp_client.connect(to_ip, to_port, from_port)
        result_str = 'successfully' if result else 'unsuccessfully'
        print(f'{self.to_str(from_port)}: {result_str} connected to server {to_ip}:{to_port}')
        return result

    def successfully_connect_of_client(self, from_ip, from_port, to_port):
        print(f'{self.to_str(to_port)}: connection from client {from_ip}:{from_port}')

    def send(self, to_ip, to_port, message, from_port=None):
        if not from_port:
            from_port = self._ports[0]

        print(f'{self.to_str(from_port)}: send to server {to_ip}:{to_port} message="{message}"')
        self.tcp_client.send(to_ip, to_port, from_port, message)

    def request_for_connect(self, from_ip, from_port, to_port):
        print(f'{self.to_str(to_port)}: received connection request from client {from_ip}:{from_port}')

    def receive_ack_from_server(self, from_ip, from_port, to_port):
        print(f'{self.to_str(to_port)}: server {from_ip}:{from_port} got message and sent "ack"')

    def not_receive_ack(self, from_ip, from_port, to_port):
        print(f'{self.to_str(to_port)}: timeout of wait the datagram with flag "ack" from client '
              f'{from_ip}:{from_port}')

    def receive_rst(self, from_ip, from_port, to_port):
        print(f'{self.to_str(to_port)}: received rst flag from {from_ip}:{from_port}')

    def receive_message(self, from_ip, from_port, to_port, message):
        print(f'{self.to_str(to_port)}: received from client {from_ip}:{from_port} message="{message}"')

    def client_is_not_connected(self, from_ip, from_port, to_port):
        print(f'{self.to_str(to_port)}: client {from_ip}:{from_port} not connected')
