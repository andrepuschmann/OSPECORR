#!/bin/bash
if ([ ! $1 ])
then
	echo "Please call with an interface as parameter."
    echo "E.g. ./setup_aodv.sh tap0"
	exit
fi
IFACE=$1
FILENAME=local.click
MAC=$(/sbin/ifconfig $IFACE | awk '/HWaddr/{print $5}' )
IP=$(/sbin/ifconfig $IFACE | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}' )

# print on stdout
echo "MAC:" $MAC
echo "IP:" $IP

# write to local.click
echo "AddressInfo(" > $FILENAME
echo "	fake ${IP}/24 $MAC" >> $FILENAME
echo ");" >> $FILENAME

# delete route
sudo route del -net 10.0.0.0 netmask 255.255.255.0 $1
sudo route del -net 10.0.0.0 netmask 255.0.0.0 $1
