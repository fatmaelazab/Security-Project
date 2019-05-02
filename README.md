# Security-Project
1) To run the project :

- Run the server.py file
- Run the client.py file as many times as the number of clients you would like to create
- Enter a unique name for each user and enter a password to start the chatting process

2) Libraries imported:

- tkinter 
- threading
- messagebox from tkinter
- * from socket 
- time
-  sys
-  cryptography
- base64
- os
- default_backend from cryptography.hazmat.backends
- hashes from cryptography.hazmat.primitives 
- PBKDF2HMAC from cryptography.hazmat.primitives.kdf.pbkdf2 
- Fernet  from cryptography.fernet 
- lsb  from stegano
- psnr from sewar.full_ref 
- cv2


if any of the above dependencies raised a module error , simply install it by running the command:  pip install then write the name of the module in the terminal

3) Make sure to specify a valid path for the steganography image where you’re going to hide the messages in the server.py file as well as choosing a valid path in the client side to write in it the image that will be used to reveal the hidden text
