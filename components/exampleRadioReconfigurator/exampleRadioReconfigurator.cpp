//
// Copyright 2014, Andre Puschmann <andre.puschmann@tu-ilmenau.de>
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//

#include <boost/program_options.hpp>
#include <boost/thread.hpp>
#include <boost/format.hpp>
#include <iostream>
#include <unistd.h>
#include <cstdio>
#include "sclhelper.hpp"
#include "OspecorrHelper.h"

namespace po = boost::program_options;

int main(int argc, char *argv[])
{
    //variables to be set by po
    std::string enginename, componentname, parametername;
    double gain_start, gain_stop, gain_step;
    int delay;

    //setup the program options
    po::options_description desc("Allowed options");
    desc.add_options()
        ("help", "help message")
        ("gainstart", po::value<double>(&gain_start)->default_value(0), "TX chain gain start value")
        ("gainstop", po::value<double>(&gain_stop)->default_value(30), "TX chain gain stop value")
        ("gainstep", po::value<double>(&gain_step)->default_value(0.5), "TX chain gain step value")
        ("delay", po::value<int>(&delay)->default_value(250), "Delay between reconfigurations")
        ("enginename", po::value<std::string>(&enginename)->default_value("phyengine1"), "Engine name containing the TX component")
        ("componentname", po::value<std::string>(&componentname)->default_value("usrptx1"), "Component name of the TX component")
        ("parametername", po::value<std::string>(&parametername)->default_value("gain"), "Parameter name of the component")
        ("dilv", "specify to disable inner-loop verbose")
    ;
    po::variables_map vm;
    po::store(po::parse_command_line(argc, argv, desc), vm);
    po::notify(vm);

    //print the help message
    if (vm.count("help")){
        std::cout << boost::format("exampleRadioReconfigurator %s") % desc << std::endl;
        std::cout <<
        "    This is a simple demo application that shows how to reconfigure a running Iris instance\n"
        "    using SCL, a ZeroMQ/ProtocolBuffers-based IPC middleware.\n\n"
        "    The application periodically reconfigures the gain setting of the Tx component in Iris.\n"
        << std::endl;
        return ~0;
    }

    bool verbose = vm.count("dilv") == 0;
    
    // compute simple gain table with ramp shape
    std::vector<double> gain_table;
    for (double i = gain_start; i < gain_stop; i+=gain_step) {
        gain_table.push_back(i);
    }
    
    std::cout << boost::format("exampleRadioReconfigurator") << std::endl << std::endl;
    std::cout << boost::format("Gain table contain %d entries.") % (gain_table.size()) << std::endl;
    std::cout << boost::format("Running periodic reconfiguration, stop with Ctrl+C ..") << std::endl;    
    
    // now iterate over table and reconfigure radio
    while (true) {
        std::vector<double>::iterator it;
        for (it = gain_table.begin(); it != gain_table.end(); it++) {
            OspecorrHelper::reconfigureRadioParameter(enginename,
                                                      componentname,
                                                      parametername,
                                                      boost::lexical_cast<std::string>(*it));      
            
            boost::this_thread::sleep(boost::posix_time::milliseconds(delay));
      }
    }
 
    // we'll never reach this
    std::cout << "The end." << std::endl;
    return 0;
}
