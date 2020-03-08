#!/usr/bin/env python3

import sqlite3
import sys

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




# There needs to be two types of tables holding sensor data
# "self" and "peer", these will be distinguished by being placed
# in two separate database files
# The table format:
# Table name will be "server_id_<unique numerical id of server>"
# | Entry Index | Sensor Index | Sensor Type | Sensor Data | Checksum of previous fields |

def main():
	print("In main")
	if check_if_self_table_exists():
		print("Table exists")
		insert_bogus_sensor_data()
	else:
		print("Table does not exist, create it")
		create_initial_table()
		insert_bogus_sensor_data()
	
if __name__ == "__main__":
	main()


