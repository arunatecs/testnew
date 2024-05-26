import base64							
client_string = "23RT3W:62a6d3d5ca1454c344b04e46aba74142"							
client_string_bytes = client_string.encode("ascii")							
base64_bytes = base64.b64encode(client_string_bytes)							
							
base64_string = base64_bytes.decode("ascii")							
							
print(base64_string)						