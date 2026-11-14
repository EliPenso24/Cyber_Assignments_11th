# 2.6 Encryption and TCP Client/Server

- `main.py`: a version of the encryption program (`encrypt` or `decrypt`, with `encrypted_msg.txt` and `logs/program.log`) where the character table is set up in a `createdata()` function.
- `server 2.6`: a TCP server on port 1002. It answers `NAME` with "PARAKALO", `RAND` with a random number from 1 to 10, `TIME` with the current date and time, and `EXIT` with "Cutting Contact". Any other request gets "Illegal action". It logs to `logsserver/program.log`.
- `user 2.6`: a client that asks for an action, sends it to 127.0.0.1:1002 and prints the response, until you enter `EXIT`. It logs to `logsuser/program.log`.
