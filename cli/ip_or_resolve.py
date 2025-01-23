import re
import socket


def is_ip_address(input_string):
    # Regular expression to match IPv4 addresses
    ipv4_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
    # Regular expression to match IPv6 addresses
    ipv6_pattern = re.compile(r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$')

    if ipv4_pattern.match(input_string) or ipv6_pattern.match(input_string):
        return True
    return False


def resolve_hostname(hostname):
    try:
        return socket.gethostbyname(hostname)
    except socket.error:
        return None


if __name__ == "__main__":
    user_input = input("Enter an IP address or hostname: ")

    if is_ip_address(user_input):
        print(f"{user_input} is an IP address.")
    else:
        ip_address = resolve_hostname(user_input)
        if ip_address:
            print(f"The IP address for {user_input} is {ip_address}.")
            print(ip_address.__class__)
        else:
            print(f"Could not resolve hostname: {user_input}.")
