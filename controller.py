#!/usr/bin/env python
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public Licens
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-

import sys
import socket

def Main():
	server_list = []
	port = 8000
	if sys.argv[1] == "--servers":
		server_str = sys.argv[2]
		server_list = server_str.split(",")

	for ip in server_list:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((ip,port))
		data = s.recv(1024)
		data = str(data.decode('ascii'))
		print("Server: %s is %s" % (ip,data))
		s.close()

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("You must specify the servers to check the status for, give a comma separated list of ip addresses:\n--server <IP1>,<IP2>,...<IPn>")
		sys.exit()
	Main()
