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
import time

sensor_index_lock = threading.Lock()
db_sync_lock = threading.Lock()

current_index=0
NoneType = type(None)
server_status = "Initializing"

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

		print("Self ID:", self.server_id)
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
	global server_status
	# each new sensor thread receives a new index
	my_index = get_sensor_index()
	# wait for the server to come up before receiving any sensor data

	while server_status != "Running":
		time.sleep(1)

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

def create_peer_initial_table(peer_db):
	peer_id = peer_db.split("_")[1][:-3] # get rid of ".db"
	self_connection = sqlite3.connect(peer_db, timeout=40)
	create_table_command = """
	CREATE TABLE server_id_%s (
		entry_index INTEGER PRIMARY KEY,
		sensor_index INTEGER,
		sensor_type VARCHAR(40),
		sensor_data VARCHAR(80),
		data_checksum INTEGER);
	""" % (peer_id)
	cursor = self_connection.cursor()
	cursor.execute(create_table_command)
	self_connection.commit()
	self_connection.close()

def insert_peer_sensor_data(peer_db, sql_cmd):
	self_connection = sqlite3.connect(peer_db, timeout=40)
	cursor = self_connection.cursor()
	# If entry already exists, exception is thrown, ignore it
	try:
		cursor.execute(sql_cmd)
	except sqlite3.IntegrityError as e:
		pass
	self_connection.commit()
	self_connection.close()

def insert_from_peer_to_self(sql_cmd):
	self_connection = sqlite3.connect("self_sensor_data.db", timeout=40)
	cursor = self_connection.cursor()
	# If entry already exists, exception is thrown, ignore it
	try:
		cursor.execute(sql_cmd)
	except sqlite3.IntegrityError as e:
		pass
	self_connection.commit()
	self_connection.close()

def check_if_peer_table_exists(peer_db):
	self_connection = sqlite3.connect(peer_db, timeout=40)
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
	
	print("Peer table count for",peer_db," is %d" %(table_count))

	if table_count == 1:
		return True
	else:
		return False

def check_if_self_table_empty():
	my_id = server.server_id
	self_connection = sqlite3.connect("self_sensor_data.db", timeout=40)
	table_command = """
	SELECT COUNT(*) FROM server_id_%s
	""" % (my_id)
	cursor =self_connection.cursor()
	cursor.execute(table_command)
	result = cursor.fetchone()
	return result[0] == 0

def check_if_peer_db_empty(peer_db):
	peer_id = peer_db.split("_")[1][:-3]
	connection = sqlite3.connect(peer_db, timeout=40)
	table_command = """
	SELECT COUNT(*) FROM server_id_%s
	""" % (peer_id)
	cursor = connection.cursor()
	cursor.execute(table_command)
	result = cursor.fetchone()
	return result[0] == 0

def get_entire_peer_db(peer_db, first_index):
	peer_id = peer_db.split("_")[1][:-3]
	connection = sqlite3.connect(peer_db, timeout=40)
	table_command = """
	select * from server_id_%s where entry_index >= %d;
	""" % (peer_id, first_index)
	cursor = connection.cursor()
	cursor.execute(table_command)
	table = cursor.fetchall()
	return table;

def receive_or_sync_peer_db(c):
	while True:
		print("Listening for peer sync or identify message")
		data = c.recv(1024)
		if not data:
			print("Connection to peer has been severed.")
			break

		id_str = str(data.decode('ascii'))

		print("### id_str: ",id_str)
		params = id_str.split("_")

		msg_type = params[0]
		peer_id = params[1]
		peer_db = "peer_%s.db" % (peer_id)
		print("Peer DB file: ", peer_db)

		if check_if_peer_table_exists(peer_db) == False:
			create_peer_initial_table(peer_db)

		c.send("ACK".encode("ascii"))
		print("Sent ACK from receive_or_sync_peer_db")

		if msg_type == "IDENTIFY":
			print("Receive IDENTIFY for peer", peer_id)

			data = ''
			while True:
				data += c.recv(1024).decode('ascii')
				if not data:
					print("Connection to peer has been severed.")
					break
				elif data[-4:] == "DONE":
					c.send("DONE".encode('ascii'))
					print("Sending DONE after data all received")
					break
				
			# This creates a list of peer sensor entries that we need to
			# change to SQL query format
			data = data.split("END")[:-1]

			for entry in data:
				cur_entry = entry.strip("BEGIN").split("/")
				sql_str = '''
					INSERT INTO server_id_%s VALUES
					(%s, %s, "%s", "%s", %s)
					''' %(peer_id, cur_entry[1], cur_entry[2], cur_entry[3], cur_entry[4], cur_entry[5])
				insert_peer_sensor_data(peer_db, sql_str)

		elif msg_type == "SYNC":
			print("Received SYNC message from: ",peer_id)
			data = c.recv(1024).decode('ascii')
			if data == "RECOVER":
				if check_if_peer_db_empty(peer_db) == True:
					c.send("DONE".encode('ascii'))
				else:
					table_data = get_entire_peer_db(peer_db, 1)

					for entry in table_data:
						entry_data = format_table_entry_into_str(entry)
						c.sendall(entry_data.encode('ascii'))

					c.send("DONE".encode('ascii'))
					data = c.recv(1024).decode('ascii')
					if data == "DONE":
						print("SYNC to ",peer_id," succesful")



def controller_resp_thread():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("", 8000))
	s.listen(5)
	while True:
		c, addr = s.accept()
		c.send(server_status.encode('ascii'))
		c.close()

def get_entire_self_db(first_index):
	self_connection = sqlite3.connect("self_sensor_data.db", timeout=40)
	table_command = """
	select * from server_id_%s where entry_index >= %d;
	""" % (server.server_id, first_index)
	cursor = self_connection.cursor()
	cursor.execute(table_command)
	table = cursor.fetchall()
	return table;

def format_table_entry_into_str(entry):
	entry_str = "BEGIN/%d/%d/%s/%s/%d/END" % (entry[0], entry[1], entry[2], entry[3], entry[4])
	return entry_str

def establish_peer_connection(peer_ip):
	global server_status
	port = 5000
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connected = False
	while not connected:
		try:
			s.connect((peer_ip ,port))
			connected = True
		except Exception as e:
			time.sleep(1)
			pass


	my_id = server.server_id
	while True:
		db_sync_lock.acquire()
		if check_if_self_table_empty() == True:
			print("DB empty, sending SYNC message to one of the peers")
			msg = "SYNC_%s" % (my_id)
			s.send(str(msg).encode('ascii'))
			print("Sent ",msg)
			#TODO: IMPLEMENT THE SYNC logic if the self has empty DB
			# peer must check if db entries >0, if no, jsut send done.
			# else send bulk contents.
			data = s.recv(1024).decode('ascii')
			if data == "ACK":
				s.send("RECOVER".encode('ascii'))

			server_status = "Syncing"
			data = ''
			while True:
				data += s.recv(1024).decode('ascii')
				if not data:
					print("Connection to peer has been severed.")
					break
				elif data[-4:] == "DONE":
					s.send("DONE".encode('ascii'))
					break

			# This creates a list of peer sensor entries that we need to
			# change to SQL query format
			data = data.split("END")[:-1]
			
			if len(data) != 0:
				for entry in data:
					cur_entry = entry.strip("BEGIN").split("/")
					sql_str = '''
						INSERT INTO server_id_%s VALUES
						(%s, %s, "%s", "%s", %s)
						''' %(my_id, cur_entry[1], cur_entry[2], cur_entry[3], cur_entry[4], cur_entry[5])
					insert_from_peer_to_self(sql_str)
			
			print("### Syncing done from peer.")

		db_sync_lock.release()

		server_status = "Running"

		print("Self ID:",my_id,"Sending IDENTIFY message to peer")
		msg = "IDENTIFY_%s" %(my_id)

		s.send(str(msg).encode("ascii"))
		data = s.recv(1024)
		if not data:
			print("Connection to peer severed")
			return


		response = data.decode("ascii")
		print("Response from ",peer_ip, " is ", response)
		print("Server ID:",server.server_id," sending self DB")
		if response == "ACK":
			table_data = get_entire_self_db(1)
		else:
			break

		for entry in table_data:
			entry_data = format_table_entry_into_str(entry)
			s.sendall(entry_data.encode('ascii'))

		s.send("DONE".encode("ascii"))

		while True:
			data = s.recv(1024)
			if not data:
				print("Connection to peer severed")
				break
			if data.decode('ascii') == "DONE":
				break

		time.sleep(10)


def listen_for_peer_connections():
	host = ""
	port = 5000

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((host,port))

	s.listen(5)

	while True:
		c, addr = s.accept()
		print("Connected to peer: ", addr[0], ":", addr[1])

		start_new_thread(receive_or_sync_peer_db, (c,))


# There needs to be two types of tables holding sensor data
# "self" and "peer", these will be distinguished by being placed
# in two separate database files
# The table format:
# Table name will be "server_id_<unique numerical id of server>"
# | Entry Index | Sensor Index | Sensor Type | Sensor Data | Checksum of previous fields |

def main():
	server_list = []
	if sys.argv[1] == "--servers":
		server_str = sys.argv[2]
		server_list = server_str.split(",")

	# start thread that listens for peer connections
	start_new_thread(listen_for_peer_connections, ())
	# start thread that connects to peer servers
	for peer_ip in server_list:
		start_new_thread(establish_peer_connection, (peer_ip,))

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

