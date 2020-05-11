set -x
brctl addbr br0
ip link add server1 type veth peer name server1_p
ip link add server2 type veth peer name server2_p
ip link add server3 type veth peer name server3_p
ip netns add server1
ip netns add server2
ip netns add server3
ip link set server1_p netns server1
ip link set server2_p netns server2
ip link set server3_p netns server3
brctl addif br0 server1
brctl addif br0 server2
brctl addif br0 server3

ip link set dev br0 up
ip link set dev server1 up
ip link set dev server2 up
ip link set dev server3 up

ip addr add 10.0.0.1/24 dev br0
ip netns exec server1 ip link set dev server1_p up
ip netns exec server2 ip link set dev server2_p up
ip netns exec server3 ip link set dev server3_p up
ip netns exec server1 ip link set dev lo up
ip netns exec server2 ip link set dev lo up
ip netns exec server3 ip link set dev lo up
ip netns exec server1 ip addr add 10.0.0.101/24 dev server1_p
ip netns exec server2 ip addr add 10.0.0.102/24 dev server2_p
ip netns exec server3 ip addr add 10.0.0.103/24 dev server3_p

mkdir server1 server2 server3
cp sensor_simulator.py server.py server1/ 
cp sensor_simulator.py server.py server2/ 
cp sensor_simulator.py server.py server3/ 
touch server1/id_file.txt
touch server2/id_file.txt
touch server3/id_file.txt
