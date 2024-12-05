# Tests for server

import subprocess

SERVICES_IN_USE = (
    "nfs-kernel-server",
    "autofs",
    "nftables",
    "slapd"
)

ACCEPTED_FIREWALL_RULES = (
    "policy drop",
    "tcp dport 2049 accept",
    "udp dport 2049 accept"
)

required_exports = {
    "/usr/local" : ["client-1", "client-2", "gw"],
    "/home1" : ["client-1", "client-2", "gw"],
    "/home2" : ["client-1", "client-2", "gw"]
}

required_export_options = [
    "rw",
    "sync",
    "no_subtree_check",
    "root_squash"
]

def test_services():
    for service in SERVICES_IN_USE:
        result = subprocess.run("systemctl is-active " + service, shell=True)
        assert result.returncode == 0

        result = subprocess.run("systemctl is-enabled " + service, shell=True)
        assert result.returncode == 0

def test_firewall():
    for rule in ACCEPTED_FIREWALL_RULES:
        result = subprocess.run("nft list ruleset | grep '" + rule + "'", shell=True)
        assert result.returncode == 0, "Firewall does not apply this required rule: " + rule

def test_exports():
    result = subprocess.run("cat /etc/exports", shell=True, capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if line[0] == "#":
            # Skip comments in stdout
            continue

        for host_and_permissions in line.split()[1:]:
            # check that the directory and who it is being exported to is specified
            directory = line.split()[0]
            host = host_and_permissions.split("(")[0]
            try:
                required_hosts = required_exports[directory]
                required_hosts.remove(host)
            except:
                assert False, "You are using an unspecified export: " + directory + "->" + host

            if len(required_hosts) == 0:
                del required_exports[directory]
            
            options = host_and_permissions.split("(")[1]
            # check that the options are specified
            for required_option in required_export_options:
                assert required_option in options, "You have not included the option \"" + required_option + "\" for: " + directory + "->" + host

    if len(required_exports) != 0:
        device_missing_export = list(required_exports.keys())[0] 
        assert False, "You have not included the required export: " + device_missing_export + "->" + required_exports[device_missing_export][0]