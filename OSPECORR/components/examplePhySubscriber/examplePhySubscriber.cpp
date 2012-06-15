#include <iostream>
#include <boost/smart_ptr.hpp>
#include "sclhelper.hpp"
#include "phy.pb.h"

using namespace std;
using namespace phy;

int main()
{
    boost::shared_ptr< SocketMap > socketMap(new SocketMap("ExampleModule"));
    boost::shared_ptr< sclGate > gate(new sclGate(socketMap.get(), "phyevent"));
    
    // give SCL some time to startup
    sleep(1);

    cout << "Now listening for incoming events .." << endl;
    while (true)
    {
        PhyMessage stats;
        gate->recvProto(stats);
        cout << "RSSI: " << stats.rssi() << endl;
        cout << "Is channel free? " << ((stats.state() == IDLE) ? true : false) << endl;
    }
    
    return 0;
}
