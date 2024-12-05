# Tests for server, client-1 and client-2

import subprocess

SERVICES_IN_USE = (
    "autofs",
    "nfs-client.target",
    "nftables",
    "nslcd",
    "nscd"
)

STATICLY_MOUNTED_DIRECTORIES = [
    "/usr/local"
]

def test_services():
    for service in SERVICES_IN_USE:
        result = subprocess.run("systemctl is-active " + service, shell=True)
        assert result.returncode == 0

        result = subprocess.run("systemctl is-enabled " + service, shell=True)
        assert result.returncode == 0

def test_static_mounts():
    for directory in STATICLY_MOUNTED_DIRECTORIES:
        result = subprocess.run("cat /etc/fstab | grep server:" + directory, shell=True, capture_output=True, text=True)
        for line in result.stdout:
            if line[0] != "#":
                assert True
                break
        else:
            assert False, "You have not included this directory in /etc/fstab: " + directory

def test_ldap_for_autofs():
    result = subprocess.run("cat /etc/nsswitch.conf | grep automount | grep ldap", shell=True)
    assert result.returncode == 0