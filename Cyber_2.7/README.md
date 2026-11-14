# File Operations Client/Server

A TCP client and server that run file commands over a JSON protocol.

- `protocol.py`: builds and parses the JSON requests and responses. Every message ends with `<END>`. Commands: DIR, DELETE, COPY, EXECUTE, TAKE_SCREENSHOT, SEND_PHOTO, EXIT. It includes assertion tests.
- `server_2.7.py`: listens on 127.0.0.1:6767 and runs the commands. Uses `pyautogui` for screenshots.
- `client_2.7.py`: connects to the server and sends commands.

`Protocol Explanation` describes the message format and `Sequence Diagram.png` shows the flow.
