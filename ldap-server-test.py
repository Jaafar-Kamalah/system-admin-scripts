# Tests for server

import subprocess

ACCEPTED_FIREWALL_RULES = (
    "policy drop",
    "tcp dport 389 accept"
)

def test_firewall():
    for rule in ACCEPTED_FIREWALL_RULES:
        result = subprocess.run("nft list ruleset | grep '" + rule + "'", shell=True)
        assert result.returncode == 0, "Firewall does not apply this required rule: " + rule

def test_ldap_server_services_active():
    result = subprocess.run("systemctl is-active slapd", shell=True)
    assert result.returncode == 0

def test_ldap_server_services_enabled():
    result = subprocess.run("systemctl is-enabled slapd", shell=True)
    assert result.returncode == 0