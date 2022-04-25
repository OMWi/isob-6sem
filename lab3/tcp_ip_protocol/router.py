import time

db = {}


def register(client):
    ip_client = client.tcp_client.ip_client
    db[ip_client.ip] = ip_client


def send(ip_data, is_wait=False):
    ip = ip_data.receive_ip
    if ip in db:
        ip_client = db[ip]
        ip_client.get(ip_data)
    elif is_wait:
        time.sleep(0.3)
