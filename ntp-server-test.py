# Tests for gw

import subprocess

ntp_sources = [
    "0.se.pool.ntp.org",
    "1.se.pool.ntp.org",
    "2.se.pool.ntp.org",
    "3.se.pool.ntp.org",
]

# key: type of restriction, value: flags it must have or must not have if it starts with "!"
required_restrictions = {
    "default" : ["ignore"],
    "192.168.1.0" : ["mask 255.255.255.0", "nomodify", "!ignore"],
    "127.0.0.1" : ["!ignore"],
    "::1" : ["!ignore"],
    "source" : ["nomodify", "!ignore"]
}

ACCEPTED_FIREWALL_RULES = (
    "policy drop",
    "udp dport 123 accept"
)

def test_firewall():
    for rule in ACCEPTED_FIREWALL_RULES:
        result = subprocess.run("nft list ruleset | grep '" + rule + "'", shell=True)
        assert result.returncode == 0, "Firewall does not apply this required rule: " + rule

def test_ntp_sources():
    result = subprocess.run("cat /etc/ntp.conf | grep -E \"server|pool\"", shell=True, capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if line[0] == "#":
            # Skip comments in stdout
            continue

        for source in ntp_sources:
            if line.split()[1] == source:
                ntp_sources.remove(source)
                break
        else:
            # Loop did not break -> NTP server is using unlisted source
            assert False, "NTP server is using a unlisted source: " + line

    if len(ntp_sources) != 0:
        assert False, "NTP sources is not using these listed servers: " + str(ntp_sources)
    else:
        assert True

def test_ntp_restrictions():
    result = subprocess.run("cat /etc/ntp.conf | grep restrict", shell=True, capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if line[0] == "#":
            # Skip comments in stdout
            continue
        
        restriction_type = line.split()[1]
        try:
            required_flags = required_restrictions[restriction_type]
        except:
            assert False, "You have included a unexpeced restriction: restrict " + restriction_type

        for required_flag in required_flags:
            if required_flag[0] == "!":
                # If the required_falg starts with "!" the rest of the flag string should not be in the line
                required_flag = required_flag[1:]
                if required_flag in line:
                    assert False, "\"restrict " + restriction_type + "\" contains illegal flag: " + required_flag
            else:
                if required_flag not in line:
                    assert False, "\"restrict " + restriction_type + "\" does not contain flag: " + required_flag
    
        del required_restrictions[restriction_type]

    if len(required_restrictions) != 0:
        assert False, "You have not included restriction: restrict " + list(required_restrictions.keys())[0]
    else:
        assert True