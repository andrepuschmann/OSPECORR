#!/bin/sh
if ([ ! $1 ] || [ ! $2 ])
then
	echo "Please call with an IP address and the device type as parameter."
    echo "E.g. ./setup_tuntap.sh 10.0.0.1 tap0"
	exit
fi

if [ ! -e /dev/net/tun ]
then
	echo "Create /dev/net/tun"
    sudo mknod /dev/net/tun c 10 200
else
	echo "/dev/net/tun already exists"
fi

sudo openvpn --mktun --dev $2
echo "Create $2 virtual network device"
sudo ifconfig $2 $1
echo "Configure IP $1 for device $2"
echo "Set MTU to 8192"
sudo ifconfig $2 mtu 8192
sudo ip route add 10.0.0.0/24 dev $2
echo "Done!"
