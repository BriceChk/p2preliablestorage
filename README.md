#  p2preliablestorage: a simple implementation of a P2P protocol between servers sharing sensor data

So far this is still in the Proof of Concept (PoC) phase.

We have the following files:

```
server.py
sensor_simulator.py
web_monitor/views.py
```

To start the server simply execute the server.py script:

```bash
$ ./server.py
```

#### Sensor simulator usage

In other terminals you can execute separate instances of the `sensor_simulator.py` script.
Running this script without any parameters gives the following output:

```bash
$ ./sensor_simulator.py
You must specify the type of sensor data to simulate.
Available options:
--temp
--pressure
--humidity
```

Using the `--temp` flag the simulator script will initiate a TCP connection to the server
script and start sending each 2 second intervals some randomly generated temperature data:

```bash
$ ./sensor_simulator.py --temp
Sending Temperature,39C,2020-04-20 23:20:18.231325
Sending Temperature,34C,2020-04-20 23:20:20.233264
Sending Temperature,39C,2020-04-20 23:20:22.235523
Sending Temperature,25C,2020-04-20 23:20:24.237794
```

Using the `--pressure` flag the simulator script will initiate a TCP connection to the server
script and start sending each 2 second intervals some randomly generated temperature data:

```bash
$ ./sensor_simulator.py --pressure
Sending Atm. Pressure,1.798 atm,2020-04-20 23:25:27.387164
Sending Atm. Pressure,4.146 atm,2020-04-20 23:25:29.389375
Sending Atm. Pressure,3.325 atm,2020-04-20 23:25:31.391742
Sending Atm. Pressure,3.827 atm,2020-04-20 23:25:33.394127
```

Using the `--humidity` flag the simulator script will initiate a TCP connection to the server
script and start sending each 2 second intervals some randomly generated temperature data:

```bash
$ ./sensor_simulator.py --humidity
Sending Humidity,15% RH,2020-04-20 23:25:50.610889
Sending Humidity,72% RH,2020-04-20 23:25:52.613108
Sending Humidity,35% RH,2020-04-20 23:25:54.615362
Sending Humidity,37% RH,2020-04-20 23:25:56.617709
```

You can start multiple instances of this `sensor_simulator.py` script and server.py will receive
and store the sensor data from all of them into the `self_sensor_data.db` database file.

#### Database

This database file is an sqlite3 database and it can be queried directly with the sqlite3 tool:

```sqlite
sqlite> .tables
server_id_b0fb648612d04a8c9ee69a218704abe0

sqlite> select * from server_id_b0fb648612d04a8c9ee69a218704abe0;

90|3|Temperature|39C 2020-04-20 23:20:18.231325|0
91|3|Temperature|34C 2020-04-20 23:20:20.233264|0
92|3|Temperature|39C 2020-04-20 23:20:22.235523|0
93|3|Temperature|25C 2020-04-20 23:20:24.237794|0
94|4|Atm. Pressure|1.798 atm 2020-04-20 23:25:27.387164|0
95|4|Atm. Pressure|4.146 atm 2020-04-20 23:25:29.389375|0
96|4|Atm. Pressure|3.325 atm 2020-04-20 23:25:31.391742|0
97|4|Atm. Pressure|3.827 atm 2020-04-20 23:25:33.394127|0
98|5|Humidity|15% RH 2020-04-20 23:25:50.610889|0
99|5|Humidity|72% RH 2020-04-20 23:25:52.613108|0
100|5|Humidity|35% RH 2020-04-20 23:25:54.615362|0
101|5|Humidity|37% RH 2020-04-20 23:25:56.617709|0
```

The next step is to implement the P2P protocol in which we have 2 instances of such servers,
and they will share each other's sensor data and into "peer" tables, most probably into
a different database file (or files). Before we do that we must implement data integrity
checks so as to ensure that the data we send between the servers is not corrupted.

#### Monitoring the servers

The monitoring system for this project is a webpage based on Flask. To run it, use this command:

```bash
$ ./web_monitor/views.py --servers <IP1,IP2,...,IPn>
```

The `--servers` option is followed by the IP addresses of the servers to monitor, separated by a comma.

You will get this kind of output:

```bash
$ ./web_monitor/views.py --servers 192.168.1.42,192.168.1.69
[INFO] Started data refresh thread
[INFO] Updating data...
 * Serving Flask app "views" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    [INFO] Server '192.168.1.42' is UP
    [INFO] Server '192.168.1.69' is UP
[INFO] Data updated.
```

The monitoring system will refresh server status every 5 seconds, and can tell if the host is offline (timeout), if an IP address is not correct, or if any other exception is thrown. Otherwise the status sent by `servers.py` is shown. The console tells where the web server is running (http://127.0.0.1:5000 in this case).

