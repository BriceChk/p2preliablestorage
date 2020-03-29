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

import socket
import time
from datetime import datetime
import random
import sys

def Main():
	# local host IP '127.0.0.1'
	host = '127.0.0.1'

	# Define the port on which you want to connect
	port = 12345

	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

	# connect to server on local computer
	s.connect((host,port))

	while True:
		# message you send to server
		timestamp = datetime.now()
		temp_string=""

		# The "," shall serve as a token to separate
		# the fields of each sensor reading
		if sys.argv[1] == "--temp":
			random_temp = random.randrange(20, 40)
			temp_string = "Temperature,"
			temp_string+=str(random_temp)
			temp_string+="C,"
			temp_string+=str(timestamp)
		if sys.argv[1] == "--pressure":
			random_pressure = round(random.uniform(1,5),3)
			temp_string = "Atm. Pressure,"
			temp_string+=str(random_pressure)
			temp_string+=" atm,"
			temp_string+=str(timestamp)
		if sys.argv[1] == "--humidity":
			random_humidity = random.randrange(1,100)
			temp_string = "Humidity,"
			temp_string+=str(random_humidity)
			temp_string+= "% RH,"
			temp_string+=str(timestamp)

		print("Sending %s" %(temp_string))
		s.send(temp_string.encode('ascii'))
		time.sleep(2)

	# close the connection
	s.close()

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("You must specify the type of sensor data to simulate.\nAvailable options:\n--temp\n--pressure\n--humidity")
		sys.exit()
	Main()
