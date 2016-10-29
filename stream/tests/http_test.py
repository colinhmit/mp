from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import json
import urlparse



class S(BaseHTTPRequestHandler):

    def do_GET(self):
        print self.path[0:8]
        print self.path[8:]
        print self.path[0:8] == '/stream/'
        self.wfile.write(json.dumps('test'))

def run(server_class=HTTPServer, handler_class=S, port=8000):
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()