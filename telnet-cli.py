import telnetlib

IP = "localhost"
PORT = "999"
tn = telnetlib.Telnet(IP, PORT)

tn.write("HELLO WORLD\n")
print(tn.read_all())