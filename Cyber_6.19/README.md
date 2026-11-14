# Port Scanner

`6.19.py` runs a TCP SYN (half-open) scan on a target IP using `scapy`. It asks for the IP and scans ports 20 to 1024. A SYN+ACK reply marks a port open and the scanner then sends a RST. It validates the IP address and port range, handles Ctrl+C, and logs to `scanner.log` and the console.
