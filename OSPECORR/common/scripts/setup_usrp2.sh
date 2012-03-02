#!/bin/sh
echo "Adjusting network receive and transmit buffer."
sudo sysctl -w net.core.wmem_max=1048576
sudo sysctl -w net.core.rmem_max=50000000
