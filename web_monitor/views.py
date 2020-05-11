#!/usr/bin/env python

from flask import Flask, render_template
import sys
import socket
from time import sleep
from _thread import start_new_thread

app = Flask(__name__)
port = 8000

@app.route('/')
def index(): 
    return render_template('index.html', servers=monitor.servers, monitor_status=monitor.status)

class Monitor():
    
    def init(self, ip_list = []):
        self.ip_list = ip_list
        self.servers = {}
        self.status = "IDLE"
        start_new_thread(self.data_refresh_thread, (self,))

    def data_refresh_thread(self, monitor):
        print("[INFO] Started data refresh thread")
        while True:
            monitor.status = "Updating data"
            print("[INFO] Updating data...")
            for ip in monitor.ip_list:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                try:
                    s.connect((ip,port))
                except TimeoutError:
                    print("    [ERROR] Server '" + ip + "' timed out")
                    monitor.servers[ip] = "Timeout"
                    continue
                except socket.gaierror:
                    print("    [ERROR] Server '" + ip + "' is invalid")
                    monitor.servers[ip] = "Invalid IP address"
                    continue
                except:
                    print("    [ERROR] Server '" + ip + "' thrown an unhandled error")
                    monitor.servers[ip] = "Down"
                    continue

                data = s.recv(1024)
                data = str(data.decode('ascii'))
                monitor.servers[ip] = data
                print("    [INFO] Server '%s' is %s" % (ip,data))
                s.close()
            monitor.status = "IDLE (up to date)"
            print("[INFO] Data updated.")
            sleep(5)


monitor = Monitor()

def Main():
    if sys.argv[1] == "--servers":
        server_str = sys.argv[2]
        server_list = server_str.split(",")
        monitor.init(server_list)
        app.run()
       

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("You must specify the servers to monitor, give a comma separated list of ip addresses:\n--server <IP1>,<IP2>,...<IPn>")
        sys.exit()
    Main()
