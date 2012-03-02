#!/bin/sh
if [ ! $1 ]
then
	echo "please call with an ip address of the new tap device as parameter"
	exit
fi

if [ ! -e /dev/net/tun ]
then
	echo "create /dev/net/tun"
    sudo mknod /dev/net/tun c 10 200
else
	echo "/dev/net/tun already exists"
fi

sudo openvpn --mktun --dev tun0
sudo ifconfig tun0 $1
echo "set MTU to 2048"
sudo ifconfig tun0 mtu 2048
sudo ip route add 10.0.0.0/24 dev tun0
echo "done"
