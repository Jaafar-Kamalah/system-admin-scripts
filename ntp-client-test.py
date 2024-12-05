# Tests for server, client-1 and client-2

import subprocess

ntp_sources = [
    "gw"
]

# key: type of restriction, value: flags it must have or must not have if it starts with "!"
required_restrictions = {
    "-4" : [],
    "-6" : [],
    "127.0.0.1" : ["!ignore"],
    "::1" : ["!ignore"],
    "source" : ["!ignore"]
}

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

def test_ntp_server_query():
    result = subprocess.run("ntpq -p | grep gw", shell=True, capture_output=True, text=True)
    assert result.returncode == 0, "gw.local not found in ntpq -p query."

    # Test that server is answering queries:
    reach = int(result.stdout.split()[6], 8)  # octal -> decimal
    reach_binary = bin(reach)[2:] # decimal -> binary (without "0B" prefix)
    reach_binary_str = str(reach_binary)
    assert reach_binary_str[-1] == "1", "Last update from server unsucessfull. Reach: " + reach_binary_str

    # Test that server offset is reasonable:
    offset = result.stdout.split()[8]
    offset_abs = float(offset[1:])   # Remove "+"/"-" from offset
    assert offset_abs < 100.0, "Server offset higher than 100 ms."

