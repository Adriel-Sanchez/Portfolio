import pyfiglet
import socket
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import signal
import sys
from colorama import Fore, init
import ssl
import time

init(autoreset=True)

# Legal notice
print("=" * 60)
print(Fore.YELLOW + "  WARNING: UNAUTHORIZED SCANNING IS ILLEGAL")
print(Fore.YELLOW + "  This tool is for educational and authorized use only.")
print(Fore.YELLOW + "  Do NOT scan systems you do not own or have permission for.")
print("=" * 60)

consent = input(Fore.WHITE + "Do you understand and agree to proceed? (yes to continue): ")
if consent.lower() != "yes":
    print(Fore.RED + "[!] Exiting. User did not accept the terms.")
    exit()

# Handle Ctrl+C
def handle_exit(sig, frame):
    print(Fore.RED + "\n[!] Scan interrupted by user. Exiting...")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)

# Display banner
ascii_banner = pyfiglet.figlet_format("\nPort Scanner", font="slant")
for i, line in enumerate(ascii_banner.splitlines()):
    print(Fore.CYAN + line if i % 2 == 0 else Fore.MAGENTA + line)

print("=" * 50)
print("Developed by Adriel Sanchez")
print("=" * 50)

# Get and resolve target
max_resolve_attempts = 3
resolve_attempts = 0
while resolve_attempts < max_resolve_attempts:
    user_input = input("\nEnter target domain or IP: ").strip()

    if user_input.lower().endswith(".local"):
        print(Fore.YELLOW + "[!] Warning: .local domains may hang or fail due to mDNS behavior.")

    try:
        addrinfo = socket.getaddrinfo(user_input, None)[0]
        target_ip = addrinfo[4][0]
        target_family = addrinfo[0]
        try:
            reverse_hostname = socket.gethostbyaddr(target_ip)[0]
        except socket.herror:
            reverse_hostname = "No PTR record found"
        break
    except socket.gaierror:
        resolve_attempts += 1
        print(Fore.RED + f"[!] Could not resolve hostname: {user_input}")
else:
    print(Fore.RED + "[!] Failed to resolve a valid target. Exiting.")
    sys.exit(1)

# Port input
def get_valid_port(prompt, default, min_port=1, max_port=65535):
    while True:
        try:
            value = int(input(prompt) or default)
            if min_port <= value <= max_port:
                return value
        except ValueError:
            pass
        print(Fore.RED + "[!] Invalid port. Please try again.")

start_port = get_valid_port("Enter start port (Min 1): ", 1)
end_port = get_valid_port("Enter end port (Max 65535): ", 65535)

while start_port > end_port:
    print(Fore.RED + "[!] Start port must be <= End port.")
    start_port = get_valid_port("Enter start port (1-65535): ", 1)
    end_port = get_valid_port("Enter end port (1-65535): ", 65535)

# Configs
initial_timeout = 0.3
timeout = initial_timeout
max_timeout = 2.0
min_timeout = 0.2
max_threads = 200
timeout_adjust_interval = 100
timeout_fail_threshold = 70
timeout_success_threshold = 10
failed_ports = 0
scan_delay = 0.01

# Print target info
print(Fore.WHITE + f"\nResolved Target: {user_input}" + (f" -> {target_ip}" if user_input != target_ip else ""))
print(Fore.WHITE + f"Reverse DNS: {reverse_hostname}")
start_time = datetime.now()
print(Fore.WHITE + f"Scan Started At: {start_time}")
print("_" * 50)

# Common service ports
port_service_map = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 587: "SMTP (SSL)",
    993: "IMAPS", 995: "POP3S", 3306: "MySQL", 3389: "RDP", 6379: "Redis",
    445: "SMB", 5900: "VNC", 8080: "HTTP-Alt", 8000: "HTTP-Alt",
    8888: "HTTP-Alt", 161: "SNMP"
}

# Banner grabbing
def grab_banner(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(1)
        s.connect((target_ip, port))

        if port in [21, 22, 23, 25, 110, 143, 993, 995, 3306, 6379, 5900]:
            return s.recv(1024).decode('utf-8', errors='ignore')
        elif port in [80, 8080, 8000, 8888]:
            s.sendall(b"HEAD / HTTP/1.1\r\nHost: " + target_ip.encode() + b"\r\nConnection: close\r\n\r\n")
            return s.recv(1024).decode('utf-8', errors='ignore')
        elif port == 443:
            context = ssl.create_default_context()
            with context.wrap_socket(s, server_hostname=target_ip) as sslsock:
                sslsock.sendall(b"HEAD / HTTP/1.1\r\nHost: " + target_ip.encode() + b"\r\nConnection: close\r\n\r\n")
                return sslsock.recv(1024).decode('utf-8', errors='ignore')
        return ""
    except:
        return ""
    finally:
        try:
            s.close()
        except:
            pass

# TCP scanner
def scan_port(port):
    global failed_ports, timeout
    try:
        with socket.socket(target_family, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.settimeout(timeout)
            if s.connect_ex((target_ip, port)) == 0:
                banner = grab_banner(port)
                return port, banner
            else:
                failed_ports += 1
    except:
        failed_ports += 1
    finally:
        time.sleep(scan_delay)
    return None

# Main scan
def main():
    global timeout, failed_ports
    open_ports = []
    scanned = 0
    total = end_port - start_port + 1

    try:
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = {executor.submit(scan_port, p): p for p in range(start_port, end_port + 1)}

            for future in as_completed(futures):
                scanned += 1
                result = future.result()
                if result:
                    open_ports.append(result)

                # Print progress (but not timeout)
                print(Fore.CYAN + f"\rScanning {scanned}/{total} ports", end="")

                if scanned % timeout_adjust_interval == 0:
                    if failed_ports > timeout_fail_threshold:
                        timeout = min(timeout + 0.2, max_timeout)
                    elif failed_ports < timeout_success_threshold and timeout > min_timeout:
                        timeout = max(timeout - 0.1, min_timeout)
                    failed_ports = 0

        duration = datetime.now() - start_time
        print(Fore.GREEN + f"\n\n[✓] Scan complete in {duration}")
        print("=" * 50)

        if open_ports:
            print(Fore.WHITE + "Open Ports and Banners:\n")
            for port, banner in sorted(open_ports):
                service = port_service_map.get(port, "Unknown")
                print(f"{Fore.GREEN}Port {port} ({service}) is open.")
                print(f"{'  Banner: ' + banner if banner else '  No banner retrieved'}\n")
        else:
            print(Fore.RED + "No open ports found.")

    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Scan interrupted by user.")
    except socket.error as e:
        print(Fore.RED + f"\n[!] Network error: {e}")
    finally:
        print("=" * 50)
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
