# Tests for router

import subprocess

IP = "192.168.1.1"
MASK = "24"
INTERFACE_WITH_IP = "ens4"

NAME = "gw"

def test_ip_and_mask():
    result = subprocess.run("ip -4 address show dev " + INTERFACE_WITH_IP + " | grep inet", shell=True, capture_output=True, text=True)
    assert result.stdout.split()[1] == IP + "/" + MASK

def test_name():
    result = subprocess.run("hostname", capture_output=True, text=True)
    assert result.stdout.strip() == NAME

def test_port_22_open():
    result = subprocess.run("nc -z -w 1 " + NAME + " 22", shell=True)
    assert result.returncode == 0
   
def test_nft_enabled():
    result = subprocess.run("systemctl is-enabled nftables", shell=True)
    assert result.returncode == 0

def test_ping():
    result = subprocess.run("ping -c 1 10.0.2.2", shell=True)
    assert result.returncode == 0    

def test_ip_forwarding():
    result = subprocess.run("cat /proc/sys/net/ipv4/ip_forward", shell=True, capture_output=True, text=True)
    assert result.stdout.strip() == "1"

def test_ip_masquerade():
    result = subprocess.run("nft list table nat | grep masquerade", shell=True, capture_output=True, text=True)
    assert result.returncode == 0
