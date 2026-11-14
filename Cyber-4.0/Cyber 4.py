"""
HTTP Server with Timing and Connection Information
Author: Barak Gonen and Nir Dweck, modified by Eli Penso
Purpose: HTTP server that includes timing and connection metadata in responses
I added more features to the header response:Date, Connection Type, Server and eve Response Time.
"""
import os
import socket
import logging
from datetime import datetime
import time

QUEUE_SIZE = 10
IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 2
WEBROOT = r"C:\WEBROOT"
DEFAULT_URL = '/index.html'

HTTP_RESPONSE_200 = "HTTP/1.1 200 OK\r\n"
HTTP_RESPONSE_302 = "HTTP/1.1 302 Found\r\nLocation: {}\r\n"
HTTP_RESPONSE_400 = "HTTP/1.1 400 Bad Request\r\n"
HTTP_RESPONSE_403 = "HTTP/1.1 403 Forbidden\r\n"
HTTP_RESPONSE_404 = "HTTP/1.1 404 Not Found\r\n"
HTTP_RESPONSE_500 = "HTTP/1.1 500 Internal Server Error\r\n"

CONTENT_TYPE_HTML = "Content-Type: text/html; charset=utf-8\r\n"
CONTENT_TYPE_JPG = "Content-Type: image/jpeg\r\n"
CONTENT_TYPE_CSS = "Content-Type: text/css\r\n"
CONTENT_TYPE_JS = "Content-Type: text/javascript; charset=UTF-8\r\n"
CONTENT_TYPE_TXT = "Content-Type: text/plain\r\n"
CONTENT_TYPE_ICO = "Content-Type: image/x-icon\r\n"
CONTENT_TYPE_GIF = "Content-Type: image/gif\r\n"
CONTENT_TYPE_PNG = "Content-Type: image/png\r\n"
HTTP_HEADER_END = "\r\n"

REDIRECTION_DICTIONARY = {
    '/moved/': '/',
}

BINARY_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.ico')


def get_current_timestamp():
    """
    Get current timestamp in HTTP date format (RFC 7231).
    Returns: str: Date in format "Day, DD Mon YYYY HH:MM:SS GMT"
    """
    from email.utils import formatdate
    return formatdate(timeval=None, localtime=False, usegmt=True)


def build_header(status, content_type, content_length, connection_type='close', response_time_ms=None):
    """
    Build the HTTP response header with timing and connection information.
    Args:
        status (str): HTTP status line (e.g., "HTTP/1.1 200 OK\r\n")
        content_type (str): Content-Type header
        content_length (int): Length of the response body in bytes
        connection_type (str): Connection type ('close' or 'keep-alive')
        response_time_ms (float): Response time in milliseconds
    Returns:
        str: Complete HTTP response header
    """
    header = status
    header += f"Date: {get_current_timestamp()}\r\n"
    header += f"Server: EliHTTP/1.0 (Python)\r\n"
    header += content_type
    header += f"Content-Length: {content_length}\r\n"
    header += f"Connection: {connection_type}\r\n"
    if response_time_ms is not None:
        header += f"X-Response-Time: {response_time_ms:.2f}ms\r\n"
    header += HTTP_HEADER_END
    return header


def get_file_data(file_name):
    """
    Read a file from WEBROOT and return its contents.
    Args:
        file_name (str): Requested file path relative to WEBROOT
    Returns:
        bytes or str: File content
    Raises:
        FileNotFoundError: If the file does not exist or path is invalid
    """
    full_path = os.path.join(WEBROOT, file_name.lstrip('/'))
    real_path = os.path.abspath(full_path)
    real_root = os.path.abspath(WEBROOT)

    if not real_path.startswith(real_root):
        logging.warning(f"Directory traversal attempt: {file_name}")
        raise FileNotFoundError()

    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        logging.info(f"File not found: {file_name}")
        raise FileNotFoundError()

    _, ext = os.path.splitext(file_name.lower())
    if ext in BINARY_EXTENSIONS:
        with open(full_path, 'rb') as f:
            return f.read()
    else:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()


def handle_client_request(resource, client_socket, start_time):
    """
    Handle a single client request and send response with timing information.
    Args:
        resource (str): The requested URI path
        client_socket (socket.socket): Client socket for sending the response
        start_time (float): Request start time (from time.time())
    """
    uri = DEFAULT_URL if resource in ('', '/') else resource
    logging.info(f"Handling request for URI: {uri}")

    # Calculate response time
    def send_with_timing(status, content_type, body1):
        response_time_ms1 = (time.time() - start_time) * 1000
        header = build_header(status, content_type, len(body1), 'close', response_time_ms1)
        client_socket.send(header.encode() + body1)
        logging.info(f"Response sent in {response_time_ms1:.2f}ms")

    # Special URIs
    if uri == '/forbidden/':
        body = b"403 Forbidden"
        send_with_timing(HTTP_RESPONSE_403, CONTENT_TYPE_HTML, body)
        return

    if uri == '/error/':
        body = b"500 Internal Server Error"
        send_with_timing(HTTP_RESPONSE_500, CONTENT_TYPE_HTML, body)
        return

    if uri in REDIRECTION_DICTIONARY:
        redirect_to = REDIRECTION_DICTIONARY[uri]
        response_time_ms = (time.time() - start_time) * 1000
        redirect_response = HTTP_RESPONSE_302.format(redirect_to)
        redirect_response += f"Date: {get_current_timestamp()}\r\n"
        redirect_response += f"Server: EliHTTP/1.0 (Python)\r\n"
        redirect_response += f"X-Response-Time: {response_time_ms:.2f}ms\r\n"
        redirect_response += HTTP_HEADER_END
        client_socket.send(redirect_response.encode())
        logging.info(f"302 Redirect sent in {response_time_ms:.2f}ms")
        return

    try:
        data = get_file_data(uri)
        _, ext = os.path.splitext(uri.lower())
        content_types = {
            '.html': CONTENT_TYPE_HTML,
            '.jpg': CONTENT_TYPE_JPG,
            '.jpeg': CONTENT_TYPE_JPG,
            '.css': CONTENT_TYPE_CSS,
            '.js': CONTENT_TYPE_JS,
            '.txt': CONTENT_TYPE_TXT,
            '.ico': CONTENT_TYPE_ICO,
            '.gif': CONTENT_TYPE_GIF,
            '.png': CONTENT_TYPE_PNG
        }
        ct = content_types.get(ext, "Content-Type: application/octet-stream\r\n")
        body = data if isinstance(data, bytes) else data.encode('utf-8')
        send_with_timing(HTTP_RESPONSE_200, ct, body)
    except FileNotFoundError:
        body = b"404 Not Found"
        send_with_timing(HTTP_RESPONSE_404, CONTENT_TYPE_HTML, body)
    except PermissionError:
        body = b"403 Forbidden"
        send_with_timing(HTTP_RESPONSE_403, CONTENT_TYPE_HTML, body)
    except OSError:
        body = b"500 Internal Server Error"
        send_with_timing(HTTP_RESPONSE_500, CONTENT_TYPE_HTML, body)


def validate_http_request(request):
    """
    Validate the format of an HTTP GET request.
    Args:
        request (str): Raw HTTP request string
    Returns:
        tuple(bool, str or None): (is_valid, requested_path)
    """
    try:
        lines = request.splitlines()
        if not lines:
            return False, None
        method, path, version = lines[0].split()
        if method != 'GET' or not path.startswith('/') or version != 'HTTP/1.1':
            return False, None
        return True, path
    except (ValueError, IndexError):
        return False, None


def handle_client(client_socket, client_addr):
    """
    Handle a single client connection with timing.
    Args:
        client_socket (socket.socket): Connected client socket
        client_addr (tuple): Client address (IP, port)
    """
    start_time = time.time()
    connection_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"Client connected: {client_addr[0]}:{client_addr[1]} at {connection_time}")
    client_socket.settimeout(SOCKET_TIMEOUT)

    try:
        client_request = client_socket.recv(1024).decode('utf-8', errors='ignore')
        if not client_request:
            return
        valid_http, resource = validate_http_request(client_request)
        if valid_http:
            handle_client_request(resource, client_socket, start_time)
        else:
            response_time_ms = (time.time() - start_time) * 1000
            body = b"400 Bad Request"
            header = build_header(HTTP_RESPONSE_400, CONTENT_TYPE_HTML, len(body), 'close', response_time_ms)
            client_socket.send(header.encode() + body)
            logging.info(f"400 Bad Request sent in {response_time_ms:.2f}ms")
    except socket.timeout:
        logging.warning(f"Socket timeout for client {client_addr}")
    except Exception as e:
        logging.error(f"Unexpected error for client {client_addr}: {e}")
    finally:
        total_time = (time.time() - start_time) * 1000
        logging.info(f"Connection closed: {client_addr[0]}:{client_addr[1]} | Total time: {total_time:.2f}ms")
        client_socket.close()


def init_logs():
    """
    Initialize logging system with detailed format.
    """
    os.makedirs("LOGS", exist_ok=True)
    logging.basicConfig(
        filename='LOGS/server.log',
        filemode='w',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info("=" * 60)
    logging.info("HTTP Server Started")
    logging.info(f"Server: EliHTTP/1.0")
    logging.info(f"Listening on {IP}:{PORT}")
    logging.info(f"WEBROOT: {WEBROOT}")
    logging.info("=" * 60)


def assertions():
    """Run internal sanity checks."""
    import tempfile
    import shutil
    assert "200 OK" in HTTP_RESPONSE_200
    assert "404 Not Found" in HTTP_RESPONSE_404
    assert '.jpg' in BINARY_EXTENSIONS
    h = build_header(HTTP_RESPONSE_200, CONTENT_TYPE_HTML, 100, 'close', 15.5)
    assert HTTP_RESPONSE_200 in h
    assert CONTENT_TYPE_HTML in h
    assert "Content-Length: 100\r\n" in h
    assert "Connection: close\r\n" in h
    assert "X-Response-Time: 15.50ms\r\n" in h
    assert "Date: " in h
    assert "Server: EliHTTP/1.0" in h
    req = "GET /index.html HTTP/1.1\r\n\r\n"
    ok, path = validate_http_request(req)
    assert ok and path == '/index.html'

    tmp_dir = tempfile.mkdtemp()
    old_webroot = WEBROOT
    try:
        globals()['WEBROOT'] = tmp_dir
        f = os.path.join(tmp_dir, 'test.html')
        with open(f, 'w') as x:
            x.write('<html>Test</html>')
        data = get_file_data('/test.html')
        assert data == '<html>Test</html>'
    finally:
        globals()['WEBROOT'] = old_webroot
        shutil.rmtree(tmp_dir)
    print(" All assertions passed!")


def main():
    """
    Main server loop with connection tracking.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Enable SO_REUSEADDR to avoid "Address already in use" error
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        print(f" EliHTTP/1.0 Server listening on {IP}:{PORT}")
        print(f" Serving files from: {WEBROOT}")
        print(f" Server started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        connection_count = 0
        while True:
            client_socket, client_addr = server_socket.accept()
            connection_count += 1
            print(f" Connection #{connection_count} from {client_addr[0]}:{client_addr[1]}")
            handle_client(client_socket, client_addr)
    except KeyboardInterrupt:
        print("\n\n Server stopped by user")
        logging.info("Server stopped by user (Ctrl+C)")
    finally:
        server_socket.close()
        logging.info("Server socket closed")
        print(" Server shut down gracefully")


if __name__ == '__main__':
    init_logs()
    assertions()
    main()
