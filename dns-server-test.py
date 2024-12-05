# Tests for server

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

ACCEPTED_FIREWALL_RULES = (
    "policy drop",
    "tcp dport 53 accept",
    "udp dport 53 accept"
)

def test_firewall():
    for rule in ACCEPTED_FIREWALL_RULES:
        result = subprocess.run("nft list ruleset | grep '" + rule + "'", shell=True)
        assert result.returncode == 0, "Firewall does not apply this required rule: " + rule

def test_preferred_dns_server():
    """Tests if the first instance of nameserver in /etc/resolv.conf
    is followed by the right IP-address.
    """
    result = subprocess.run("grep -m 1 \"nameserver\" /etc/resolv.conf", 
                            shell=True, capture_output=True, text=True)
    assert result.stdout.split()[1] == DNS_SERVER_IP

def test_named_configuration():
    result = subprocess.run("named-checkconf", shell=True)
    assert result.returncode == 0

def test_zones():
    for zone in ZONES:
        result = subprocess.run("named-checkzone " + zone + " /etc/bind/zones/" + zone,
                                shell=True)
        assert result.returncode == 0

def test_named_is_active():
    result = subprocess.run("systemctl is-active named", shell=True)
    assert result.returncode == 0

def test_named_is_enabled():
    result = subprocess.run("systemctl is-enabled named", shell=True)
    assert result.returncode == 0

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