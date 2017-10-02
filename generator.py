from socket import *
from flask import Flask
from flask_restful import Resource, Api
import threading


NIC_NAME = "eth0"

class ErrorGenerator(threading.Thread):

    def __init__(self, count):
        super(ErrorGenerator, self).__init__()
        self._stop_event = threading.Event()
        self.send = False
        self.count = count

    def run(self):
        s = socket(AF_PACKET, SOCK_RAW)
        s.setsockopt(SOL_SOCKET,43,1)
        s.bind((NIC_NAME, 0))
        src_addr = "\x00\x15\x17\xea\x0a\x5c"
        dst_addr = "\x00\x22\xbd\xf8\x19\xff"
        payload = ("["*30)+"PAYLOAD"+("]"*30)
        checksum = "\x00\x00\x00\x00"
        ethertype = "\x08\x00"
        for i in range(0, self.count):
            s.send(dst_addr+src_addr+ethertype+payload+checksum)

app = Flask(__name__)
api = Api(app)

class Start(Resource):
    def post(self, count):
        t = ErrorGenerator(count)
        t.start()
        return {'status': 'generating errors'}

api.add_resource(Start, '/api/errors/<int:count>')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)