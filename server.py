#!/usr/bin/env python3
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

import sqlite3
import sys
import socket
from _thread import *
import threading

sensor_index_lock = threading.Lock()

current_index=0

def get_sensor_index():
	global current_index
	ret_index=current_index
	sensor_index_lock.acquire()
	current_index+=1
	sensor_index_lock.release()
	return ret_index

def create_initial_table():
	self_connection = sqlite3.connect("self_sensor_data.db")
	create_table_command = """
	CREATE TABLE server_id_12312313 (
		entry_index INTEGER PRIMARY KEY,
		sensor_index INTEGER,
		sensor_type VARCHAR(40),
		sensor_data VARCHAR(80),
		data_checksum INTEGER);
	"""
	cursor = self_connection.cursor()
	cursor.execute(create_table_command)
	self_connection.commit()
	self_connection.close()


def check_if_self_table_exists():
	self_connection = sqlite3.connect("self_sensor_data.db")
	show_table_command = """
		SELECT name FROM sqlite_master WHERE type='table'
		AND name='server_id_12312313'
	"""
	cursor = self_connection.cursor()
	cursor.execute(show_table_command)
	table_row = cursor.fetchone()
	self_connection.commit()
	self_connection.close()

	NoneType = type(None)
	if not isinstance(table_row, NoneType):
		return True
	else:
		return False


def insert_bogus_sensor_data():
	self_connection = sqlite3.connect("self_sensor_data.db")
	insert_table_command = """
	INSERT INTO server_id_12312313 VALUES
	(NULL, 2, "Weather", "21C rain", 23232);
	"""
	cursor = self_connection.cursor()
	cursor.execute(insert_table_command)
	self_connection.commit()
	self_connection.close()

def convert_sensor_dict_to_sql_command(sensor_dict):
	sql_insert_command_str = '''
		INSERT INTO server_id_12312313 VALUES
		(NULL, %s, "%s", "%s %s", 0)
	''' % (sensor_dict["index"],sensor_dict["sensor_type"],sensor_dict["sensor_data"],sensor_dict["timestamp"])
	return sql_insert_command_str

def insert_self_sensor_data(sql_cmd):
	self_connection = sqlite3.connect("self_sensor_data.db")
	cursor = self_connection.cursor()
	#print("SQL command: %s" %(sql_cmd))
	cursor.execute(sql_cmd)
	self_connection.commit()
	self_connection.close()

# returns a dict
def decode_sensor_reading_from_str(sensor_str, index):
	sensor_reading_list=sensor_str.split(",")
	sensor_data_dict = {"sensor_type":sensor_reading_list[0]}
	sensor_data_dict.update({"sensor_data":sensor_reading_list[1]})
	sensor_data_dict.update({"timestamp":sensor_reading_list[2]})
	sensor_data_dict.update({"index":index})
	return sensor_data_dict

def insert_sensor_str_to_table(sensor_str, index):
	sensor_dict = decode_sensor_reading_from_str(sensor_str, index)
	sql_insert_cmd = convert_sensor_dict_to_sql_command(sensor_dict)
	insert_self_sensor_data(sql_insert_cmd)


def sensor_rcv_thread(c):
	# each new sensor thread receives a new index
	my_index = get_sensor_index()
	while True:

		# data received from client
		data = c.recv(1024)
		if not data:
			print('Connection severed')
			break

		sensor_str = str(data.decode('ascii'))
		insert_sensor_str_to_table(sensor_str, my_index)
		print("Received: %s" %(sensor_str))


	# connection closed
	c.close()



# There needs to be two types of tables holding sensor data
# "self" and "peer", these will be distinguished by being placed
# in two separate database files
# The table format:
# Table name will be "server_id_<unique numerical id of server>"
# | Entry Index | Sensor Index | Sensor Type | Sensor Data | Checksum of previous fields |

def main():
	print("In main")
	# We first check if the database exists
	if not check_if_self_table_exists():
		print("Table does not exist, create it")
		create_initial_table()

	host = ""

	# reverse a port on your computer
	# in our case it is 12345 but it
	# can be anything
	port = 12345
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((host, port))
	print("socket binded to port", port)

	# put the socket into listening mode
	s.listen(5)
	print("socket is listening")

	# a forever loop until client wants to exit
	while True:

		# establish connection with client
		c, addr = s.accept()

		# lock acquired by client
		print('Connected to :', addr[0], ':', addr[1])

		# Start a new thread and return its identifier
		start_new_thread(sensor_rcv_thread, (c,))
	s.close()


if __name__ == "__main__":
	main()

