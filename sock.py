from pwn import *

def hex_bin(hex_string):
    parts = hex_string.split(":")
    r = []
    f = []
    s = []
    sum = []
    
    for part in parts:
        num = int(part, 16)
        binary = bin(num)[2:]   
        r.append(hex(num)[2:] if num > 15 else binary) 
    
    f.extend(r[1:3])    
    s.extend(r[3:6])    
    
    r[0] = hex(int(r[0], 16) + 2)[2:]
    
    sum.append(r[0]) 
    sum.extend(f)
    sum.extend(["ff", "fe"])
    sum.extend(s) 
    
    burlast = ":".join([str(item) for item in sum])  
    
    return burlast





ip = "52.79.202.17"
port = 10000

io = remote(ip,port)

io.recvuntil(b' \n ')

while True:
    b = io.recv().strip().decode()
    if "ccsCTF" in b:
        print(b)
        break
    result = hex_bin(b)
    io.send(result.encode())