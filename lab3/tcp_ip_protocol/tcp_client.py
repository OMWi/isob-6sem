import random

from tcp_ip_protocol.ip_client import IpClient


class TcpClient:
    def __init__(self, client, ip, ports):
        self._client = client
        self._ports = ports
        self._ip_client = IpClient(self, ip)
        self._is_wait = dict(map(lambda port: (port, None), ports))
        self._connect_addresses = dict(map(lambda port: (port, set()), ports))
        self._sn_ac_flags = {}

    @property
    def ip_client(self):
        return self._ip_client

    def connect(self, to_ip, to_port, from_port):
        tcpdata = self.create_tcpdata(from_port, to_port)
        tcpdata.set_syn()
        tcpdata['sn'] = random.randint(0, 10000)
        self._ip_client.send(to_ip, tcpdata)
        return (to_ip, to_port) in self._connect_addresses[from_port]

    def send(self, to_ip, to_port, from_port, message):
        tcpdata = self.create_tcpdata(from_port, to_port, message)
        flags = self._sn_ac_flags[(from_port, to_ip, to_port)]
        tcpdata['sn'] = flags[0]
        tcpdata['as'] = flags[1]
        self._ip_client.send(to_ip, tcpdata)
        self._sn_ac_flags[(from_port, to_ip, to_port)] = (flags[0] + len(message), flags[1] + 1)

    def get(self, tcpdata, from_ip):
        from_port = tcpdata.sender_port
        to_port = tcpdata.receive_port

        if to_port not in self._ports:
            pass

        elif self._is_wait[to_port]:
            if (
                (from_ip, from_port) in self._is_wait[to_port] and
                self._is_wait[to_port][(from_ip, from_port)] == (tcpdata['as'], tcpdata['sn'])
            ):
                if tcpdata['ack'] and not tcpdata['syn']:
                    self._connect_addresses[to_port].add((from_ip, from_port))
                    self._sn_ac_flags[(to_port, from_ip, from_port)] = (tcpdata['as'], tcpdata['sn'] + 1)
                    self._client.successfully_connect_of_client(from_ip, from_port, to_port)

                elif tcpdata['rst']:
                    self._is_wait[to_port] = None
                    self._client.receive_rst(from_ip, from_port, to_port)

        elif tcpdata['rst']:
            if self._sn_ac_flags[(to_port, from_ip, from_port)] == (tcpdata['as'], tcpdata['sn']):
                if (from_ip, from_port) in self._connect_addresses[to_port]:
                    self._connect_addresses[to_port].remove((from_ip, from_port))
                    del self._sn_ac_flags[(to_port, from_ip, from_port)]
                self._client.receive_rst(from_ip, from_port, to_port)

        elif tcpdata['syn'] and tcpdata['ack']:
            answer_tcpdata = self.create_tcpdata(to_port, from_port)
            answer_tcpdata.set_ack()
            answer_tcpdata['sn'] = tcpdata['as']
            answer_tcpdata['as'] = tcpdata['sn'] + 1
            self._ip_client.send(from_ip, answer_tcpdata)
            self._connect_addresses[to_port].add((from_ip, from_port))
            self._sn_ac_flags[(to_port, from_ip, from_port)] = (tcpdata['as'] + 1, tcpdata['sn'] + 1)

        elif tcpdata['syn']:
            self._client.request_for_connect(from_ip, from_port, to_port)
            answer_tcpdata = self.create_tcpdata(to_port, from_port)
            answer_tcpdata.set_syn()
            answer_tcpdata.set_ack()
            answer_tcpdata['sn'] = random.randint(0, 10000)
            answer_tcpdata['as'] = tcpdata['sn'] + 1
            self._is_wait[to_port] = {
                (from_ip, from_port): (answer_tcpdata['sn'] + 1, answer_tcpdata['as']),
            }
            self._ip_client.send(from_ip, answer_tcpdata, is_wait=True)
            if (from_ip, from_port) not in self._connect_addresses[to_port] and self._is_wait[to_port]:
                self._client.not_receive_ack(from_ip, from_port, to_port)
            self._is_wait[to_port] = None

        elif tcpdata['ack']:
            self._client.receive_ack_from_server(from_ip, from_port, to_port)

        elif (from_ip, from_port) not in self._connect_addresses[to_port]:
            self._client.client_is_not_connected(from_ip, from_port, to_port)
            tcpdata = self.create_tcpdata(to_port, from_port)
            tcpdata.set_rst()
            self._ip_client.send(from_ip, tcpdata)

        elif self._sn_ac_flags[(to_port, from_ip, from_port)] == (tcpdata['as'], tcpdata['sn']):
            message = tcpdata.message
            self._client.receive_message(from_ip, from_port, to_port, message)
            answer_tcpdata = self.create_tcpdata(to_port, from_port)
            answer_tcpdata.set_ack()
            self._ip_client.send(from_ip, answer_tcpdata)
            self._sn_ac_flags[(to_port, from_ip, from_port)] = (tcpdata['as'] + 1, tcpdata['sn'] + len(message))

    @staticmethod
    def create_tcpdata(from_port, to_port, data=None):
        return TCPData(from_port, to_port, data)


class TCPData:
    def __init__(self, from_port, to_port, data=None):
        self._data = {
            'sender_port': from_port,
            'receive_port': to_port,
            'sn': 0,
            'as': 0,
            'tcp_header_length': 160,
            'reserved_field': 0,
            'urg': 0,
            'ack': 0,
            'psh': 0,
            'rst': 0,
            'syn': 0,
            'fin': 0,
            'frame_size': 0,
            'control_sum': len(data) if data else 0,
            'urgency_indicators': 0,
            'data': data,
        }

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        self._data[key] = value

    @property
    def sender_port(self):
        return self._data['sender_port']

    @property
    def receive_port(self):
        return self._data['receive_port']

    @property
    def message(self):
        return self._data['data']

    def set_syn(self):
        self._data['syn'] = 1

    def set_ack(self):
        self._data['ack'] = 1

    def set_rst(self):
        self._data['rst'] = 1
