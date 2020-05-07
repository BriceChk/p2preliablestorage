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
import uuid
import os
import os.path
import unittest

sensor_index_lock = threading.Lock()

current_index=0
NoneType = type(None)
server_status = "UP"

class Server():
	server_id = 0
	def __init__(self):
		self_connection = sqlite3.connect("self_sensor_data.db", timeout=40)
		table_command = """
		SELECT COUNT(*) FROM sqlite_master WHERE type='table'
		"""
		cursor =self_connection.cursor()
		cursor.execute(table_command)
		table_row = cursor.fetchone()

		if not isinstance(table_row, NoneType):
			table_count = table_row[0]
		else:
			table_count = 0

		f = open("id_file.txt", "r+")
		if os.stat("id_file.txt").st_size != 0 and table_count == 0:
			self.server_id = f.readline().rstrip()
			self.create_initial_table()

		elif not table_count == 0:
			fileid = f.readline().rstrip()
			table_command = """
			SELECT name FROM sqlite_master WHERE type='table'
			"""
			cursor.execute(table_command)
			table_row = cursor.fetchone()
			tableid = table_row[0].split("_")[2]
			if fileid != tableid:
				print("id_file and table id differ, adopt table id")
				f.truncate(0)
				f.write(str(tableid) + "\n")
				self.server_id=tableid
			else:
				self.server_id = tableid
				print("id_file and table id match, do nothing")

		elif os.stat("id_file.txt").st_size == 0 and table_count==0:
			self.server_id = uuid.uuid4().hex
			f.write(str(self.server_id) + "\n")
			self.create_initial_table()

		self_connection.commit()
		self_connection.close()


	def convert_sensor_dict_to_sql_command(self, sensor_dict):
		sql_insert_command_str = '''
			INSERT INTO server_id_%s VALUES
			(NULL, %s, "%s", "%s %s", 0)
		''' % (str(self.server_id),sensor_dict["index"],sensor_dict["sensor_type"],sensor_dict["sensor_data"],sensor_dict["timestamp"])
		return sql_insert_command_str

	def insert_sensor_data(self, sql_cmd):
		self_connection = sqlite3.connect("self_sensor_data.db", timeout=40)
		cursor = self_connection.cursor()
		#print("SQL command: %s" %(sql_cmd))
		cursor.execute(sql_cmd)
		self_connection.commit()
		self_connection.close()

# returns a dict
	def decode_sensor_reading_from_str(self, sensor_str, index):
		sensor_reading_list=sensor_str.split(",")
		sensor_data_dict = {"sensor_type":sensor_reading_list[0]}
		sensor_data_dict.update({"sensor_data":sensor_reading_list[1]})
		sensor_data_dict.update({"timestamp":sensor_reading_list[2]})
		sensor_data_dict.update({"index":index})
		return sensor_data_dict

	def insert_sensor_str_to_table(self, sensor_str, index):
		sensor_dict = self.decode_sensor_reading_from_str(sensor_str, index)
		sql_insert_cmd = self.convert_sensor_dict_to_sql_command(sensor_dict)
		self.insert_sensor_data(sql_insert_cmd)

	def create_initial_table(self):
		self_connection = sqlite3.connect("self_sensor_data.db", timeout=40)
		create_table_command = """
		CREATE TABLE server_id_%s (
			entry_index INTEGER PRIMARY KEY,
			sensor_index INTEGER,
			sensor_type VARCHAR(40),
			sensor_data VARCHAR(80),
			data_checksum INTEGER);
		""" % (str(self.server_id))
		cursor = self_connection.cursor()
		cursor.execute(create_table_command)
		self_connection.commit()
		self_connection.close()

	def check_if_self_table_exists(self, id):
		self_connection = sqlite3.connect("self_sensor_data.db", timeout=40)
		show_table_command = """
			SELECT name FROM sqlite_master WHERE type='table'
			AND name= 'server_id_%s'""" % str(id)

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

class TestServerMethods(unittest.TestCase):
	def test_decoding_string(self):
		self.assertTrue(True)
	def test_create_table(self):
		self.assertTrue(True)
	def test_insert_sensor_data(self):
		self.assertTrue(True)

server = Server()

def get_sensor_index():
	global current_index
	ret_index=current_index
	sensor_index_lock.acquire()
	current_index+=1
	sensor_index_lock.release()
	return ret_index

def sensor_rcv_thread(c, server):
	# each new sensor thread receives a new index
	my_index = get_sensor_index()
	while True:

		# data received from client
		data = c.recv(1024)
		if not data:
			print('Connection severed')
			break

		sensor_str = str(data.decode('ascii'))
		server.insert_sensor_str_to_table(sensor_str, my_index)
		print("Received: %s" %(sensor_str))


	# connection closed
	c.close()

def controller_resp_thread():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("", 8000))
	s.listen(5)
	while True:
		c, addr = s.accept()
		c.send(server_status.encode('ascii'))
		c.close()
		
		


# There needs to be two types of tables holding sensor data
# "self" and "peer", these will be distinguished by being placed
# in two separate database files
# The table format:
# Table name will be "server_id_<unique numerical id of server>"
# | Entry Index | Sensor Index | Sensor Type | Sensor Data | Checksum of previous fields |

def main():
	print("In main")


	# start the controller thread
	start_new_thread(controller_resp_thread, ())
	# reverse a port on your computer
	# in our case it is 12345 but it
	# can be anything
	host = ""
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
		start_new_thread(sensor_rcv_thread, (c, server))
	s.close()


if __name__ == "__main__":
	main()

