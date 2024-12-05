# Tests for gw, client-1 and client-2

import subprocess

SERVICES_THAT_SHOULD_USE_LDAP = (
    "passwd",
    "group",
    "shadow"
)

USER_FROM_LDAP = "ldap_user"

def test_ldap_client_services_active():
    result = subprocess.run("systemctl is-active nslcd", shell=True)
    assert result.returncode == 0

    result = subprocess.run("systemctl is-active nscd", shell=True)
    assert result.returncode == 0

def test_ldap_client_services_enabled():
    result = subprocess.run("systemctl is-enabled nslcd", shell=True)
    assert result.returncode == 0

    result = subprocess.run("systemctl is-enabled nscd", shell=True)
    assert result.returncode == 0

def test_nsswitch_config():
    for service in SERVICES_THAT_SHOULD_USE_LDAP:
        result = subprocess.run("cat /etc/nsswitch.conf | grep " + service + " | grep ldap",
                                shell=True)
        assert result.returncode == 0

def test_ldapsearch():
    result = subprocess.run("ldapsearch -x", shell=True)
    assert result.returncode == 0

def test_ldap_user_exists():
    result = subprocess.run("getent passwd " + USER_FROM_LDAP, shell=True)
    assert result.returncode == 0