import socket

def sqroonet(coeffs: str,s socket.socket) -> str:
	s.sendall((coeffs + '\n').encode())
	return s.recv(128).decode().strip()
	
with socket.socket(socket.AF_INF, socket.SOCK_STREAM) as s:
	s.connect(('localhost', 1337))
	print(sqrootnet(coeffs,s))
