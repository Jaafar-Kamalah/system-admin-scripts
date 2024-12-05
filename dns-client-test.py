# Tests for gw, client-1 and client-2

import subprocess

DNS_SERVER_IP = "192.168.1.2"

ZONES = (
    "g4.example.com",
    "1.168.192.in-addr.arpa"
)

HOSTS = {
    "server": "192.168.1.2",
    "gw": "192.168.1.1",
    "client-1": "192.168.1.3",
    "client-2": "192.168.1.4"
}

def test_preferred_dns_server():
    """Tests if the first instance of nameserver in /etc/resolv.conf
    is followed by the right IP-address.
    """
    result = subprocess.run("grep -m 1 \"nameserver\" /etc/resolv.conf", 
                            shell=True, capture_output=True, text=True)
    assert result.stdout.split()[1] == DNS_SERVER_IP

def test_forward_dns_queries():
    for hostname, ip in HOSTS.items():
        result = subprocess.run("dig @" + DNS_SERVER_IP + " " + hostname + "." + ZONES[0] + " +short",
                                shell=True, capture_output=True, text=True)
        assert result.stdout.strip() == ip

def test_reverse_dns_queries():
    for hostname, ip in HOSTS.items():
        result = subprocess.run("dig @" + DNS_SERVER_IP +" -x " + ip + " +short",
                                shell=True, capture_output=True, text=True)
        assert result.stdout.strip() == hostname + "." + ZONES[0] + "."