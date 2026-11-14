# Encryption and Decryption

`main.py` takes `encrypt` or `decrypt` as a command-line argument.

- `encrypt` asks for a message, replaces each character with a number from a fixed table, and saves the numbers (comma-separated) to `encrypted_msg.txt`. It exits with an error that lists any characters the table does not support.
- `decrypt` reads `encrypted_msg.txt` and prints the original message. It handles an empty file, a missing file and invalid data.

Actions are logged to `logs/program.log`. Assertions at the end of the file test the encrypt and decrypt functions.
