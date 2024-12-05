#!/usr/bin/env python3

import sys
import subprocess
import os.path
import string
import random

def not_letters(str):
    for c in str:
        if  c < "a" or c > "z":
            # Not between a and z
            return True
    return 

def generate_random_lowercase_string(length):
    characters = string.ascii_lowercase
    return ''.join(random.choice(characters) for i in range(length))

def cleanup():
    # Remove output_file
    print("Cleanup: Removing output file")
    try:
        subprocess.run(["rm", output_file], check=True, capture_output=True)
    except Exception as e:
        print("Cleanup error:", str(e))

# Command line argument handling
if len(sys.argv) != 2:
    print("Usage:", sys.argv[0], "<input_file>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = "formatted_names"

# Check if the input file exists
if not os.path.isfile(input_file):
    print("Input file not found:", input_file)
    sys.exit(1)

# Convert file from ISO-8859-1 to ASCII//TRANSLIT
try:
    subprocess.run(["iconv", "-f", "ISO-8859-1", "-t", "ASCII//TRANSLIT", input_file, "-o", output_file],
                   check=True)
except Exception as e:
    print("File conversion led to error:")
    print(e)
    sys.exit(1)

#Create accounts
try:
    subprocess.run(["echo", "Generated Accounts:\n-------------------"], check=True)
    with open(output_file, "r") as formatted_file:
        for line in formatted_file:

            # Don't create account if line only is whitespaces
            if line.isspace():
                #print("Skipped") #debug
                continue

            # Make full name lowercase and Split into space seperated list
            line = line.lower()
            split_name = line.split()
            #print(split_name) #debug

            # Create 5 letter user name
            # Randomize user name if:
            # *First name has less than three letters
            # *Last name has less than two letters
            if len(split_name) < 2:
                user_name = generate_random_lowercase_string(5)
            else:
                first_name = split_name[0]
                last_name = split_name[1]
                if len(first_name) < 3 or len(last_name) < 2:
                    user_name = generate_random_lowercase_string(5)
                else:
                    first_name_prefix = first_name[0:3]
                    last_name_prefix = last_name[0:2]
                    if not_letters(first_name_prefix) or not_letters(last_name_prefix):
                        user_name = generate_random_lowercase_string(5)
                    else:
                        user_name = first_name_prefix + last_name_prefix

            # Give the user name a number suffix of 1
            # If user name + number suffix exists increment the number
            user_name_number = 1

            getent_result = subprocess.run(["getent", "passwd", user_name + str(user_name_number)], stdout=subprocess.DEVNULL)
            while getent_result.returncode == 0:
                user_name_number += 1
                getent_result = subprocess.run(["getent", "passwd", user_name + str(user_name_number)], stdout=subprocess.DEVNULL)

            full_user_name = user_name + str(user_name_number)
            subprocess.run(["useradd", "-m", full_user_name], check=True)
            subprocess.run(["mv", "/home/" + full_user_name, "/home1/"])

            # Generate and set password
            user_password = generate_random_lowercase_string(6)
            subprocess.run("chpasswd", input=full_user_name + ":" + user_password, text=True, check=True)
            subprocess.run("cat", input=full_user_name + " " + user_password + "\n", text=True, check=True)

            # Add user to LDAP directory:
            try:
                user_uid_result = subprocess.run(["id", "-u", full_user_name], check=True, text=True, capture_output=True)
                subprocess.run(["ldapadduser", full_user_name, "myGroup", user_uid_result.stdout.strip()], check=True, stdout=subprocess.DEVNULL)
                subprocess.run(["ldapsetpasswd", full_user_name, user_password], check=True, stdout=subprocess.DEVNULL)
                #print("Successfully added to LDAP-directory!")
            except Exception as e:
                print("Failed to add user \"" + full_user_name + "\" to LDAP-directory:")
                print (e)
except Exception as e:
    print("Account creation loop led to error:")
    print(e)
    cleanup()
    sys.exit(1)

cleanup()