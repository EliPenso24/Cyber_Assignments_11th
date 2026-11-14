"""
Port Scanner API
----------------
This module provides functionality to perform a TCP SYN Scan (Half-Open Scan)
on a target remote host to identify open ports within a specific range.

Features:
- IP address validation.
- Port range assertion and validation.
- Logging of all operations to a local file and console.
- Graceful handling of user interrupts.
"""

from scapy.layers.inet import IP, TCP
from scapy.sendrecv import sr1
import logging
import ipaddress
import os

# --- קבועים (Constants) ---
DEFAULT_START_PORT = 20
DEFAULT_END_PORT = 1024
TIMEOUT_VAL = 0.5
SYN_ACK_FLAGS = 0x12
RST_ACK_FLAGS = 0x14
MAX_PORT_VALUE = 65535
MIN_PORT_VALUE = 0

# הגדרת נתיב לקובץ הלוג באותה תיקייה של הפרויקט
current_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(current_dir, "scanner.log")

# הגדרת לוגים - כתיבה לקובץ ולמסך
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)


def validate_scan_parameters(ip_str, start_port, end_port):
    """
    Validates the input parameters for the scan.

    :param ip_str: The target IP address as a string.
    :param start_port: The starting port of the range (integer).
    :param end_port: The ending port of the range (integer).
    :return: True if the IP is valid, raises AssertionError for invalid port logic.
    """
    # בדיקת תקינות כתובת IP
    try:
        ipaddress.ip_address(ip_str)
    except ValueError:
        logger.error(f"Invalid IP address format: {ip_str}")
        return False

    # בדיקות Assert - מיועדות לתפוס שגיאות לוגיות בזמן הפיתוח
    assert isinstance(start_port, int) and isinstance(end_port, int), "Ports must be integers"
    assert MIN_PORT_VALUE <= start_port <= MAX_PORT_VALUE, f"Start port out of range"
    assert MIN_PORT_VALUE <= end_port <= MAX_PORT_VALUE, f"End port out of range"
    assert start_port <= end_port, "Start port cannot be greater than end port"

    return True


def scan_ports(target_ip, start_port=DEFAULT_START_PORT, end_port=DEFAULT_END_PORT):
    """
    Performs a TCP SYN scan on the target IP for the specified port range.

    :param target_ip: Destination IP address.
    :param start_port: Range start (default 20).
    :param end_port: Range end (default 1024).
    :return: A list of open ports found, or None if the scan was aborted.
    """
    if not validate_scan_parameters(target_ip, start_port, end_port):
        return None

    logger.info(f"Initiating scan on {target_ip} (Ports: {start_port}-{end_port})")
    open_ports = []

    try:
        for port in range(start_port, end_port + 1):
            # יצירת חבילת SYN
            packet = IP(dst=target_ip) / TCP(dport=port, flags="S")

            # שליחה והמתנה לתשובה (sr1 מחזירה חבילה אחת או None)
            response = sr1(packet, timeout=TIMEOUT_VAL, verbose=0)

            if response and response.haslayer(TCP):
                # אם קיבלנו SYN+ACK, הפורט פתוח
                if response.getlayer(TCP).flags == SYN_ACK_FLAGS:
                    logger.info(f"Port {port} is OPEN")
                    open_ports.append(port)

                    # שליחת RST לסגירת הקשר "החצי פתוח"
                    rst_packet = IP(dst=target_ip) / TCP(dport=port, flags="R")
                    sr1(rst_packet, timeout=TIMEOUT_VAL, verbose=0)

                # אם קיבלנו RST+ACK, הפורט סגור
                elif response.getlayer(TCP).flags == RST_ACK_FLAGS:
                    logger.debug(f"Port {port} is closed.")

        return open_ports

    except KeyboardInterrupt:
        logger.warning("Scan manually stopped by user.")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return None


if __name__ == "__main__":
    print(f"Logging to: {log_file_path}")
    target = input("Enter target IP to scan: ").strip()

    # הפעלת הסורק
    results = scan_ports(target)

    print("\n" + "=" * 30)
    if results is not None:
        logger.info(f"Scan summary for {target}: {len(results)} ports open.")
        print(f"Scan Finished. Open ports found: {results if results else 'None'}")
    else:
        print("Scan failed or was interrupted.")
    print("=" * 30)
