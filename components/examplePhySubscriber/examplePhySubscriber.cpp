#include <iostream>
#include "sclhelper.hpp"
#include "phy.pb.h"

using namespace std;
using namespace scl_phy;

int main()
{
    GateFactory &myFactory = GateFactory::getInstance();
    sclGate *gate = myFactory.createGate("ExampleModule", "phyevent");
    
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
