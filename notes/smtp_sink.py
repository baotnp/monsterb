"""Minimal local SMTP sink: every message is saved as a numbered .eml file. Python 3.8+, no dependencies."""
import os
import socketserver
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 1025
OUT = sys.argv[2] if len(sys.argv) > 2 else "mail-sink"
os.makedirs(OUT, exist_ok=True)
count = [len(os.listdir(OUT))]


class Handler(socketserver.StreamRequestHandler):
    def reply(self, line):
        self.wfile.write(line.encode() + b"\r\n")

    def handle(self):
        try:
            self.session()
        except ConnectionError:
            pass            # a client that hangs up (a port probe) is not an error

    def session(self):
        self.reply("220 sink ready")
        rcpt = "nobody"
        while True:
            line = self.rfile.readline()
            if not line:
                return
            cmd = line.decode(errors="replace").strip()
            word = cmd.upper()
            if word.startswith(("EHLO", "HELO", "MAIL", "RSET", "NOOP")):
                self.reply("250 OK")
            elif word.startswith("RCPT"):
                rcpt = cmd[cmd.find("<") + 1:cmd.find(">")] or rcpt
                self.reply("250 OK")
            elif word == "DATA":
                self.reply("354 end with <CRLF>.<CRLF>")
                body = []
                while True:
                    row = self.rfile.readline()
                    if row in (b".\r\n", b".\n", b""):
                        break
                    body.append(row[1:] if row.startswith(b"..") else row)
                count[0] += 1
                name = "%04d-%s.eml" % (count[0], rcpt.replace("/", "_"))
                with open(os.path.join(OUT, name), "wb") as handle:
                    handle.write(b"".join(body))
                print("saved", name, flush=True)
                self.reply("250 queued")
            elif word == "QUIT":
                self.reply("221 bye")
                return
            else:
                self.reply("502 not implemented")


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    with Server(("127.0.0.1", PORT), Handler) as server:
        print("sink on 127.0.0.1:%d, writing to %s" % (PORT, OUT), flush=True)
        server.serve_forever()
