/**
 * \file lib/utility/OspecorrHelper.h
 * \version 1.0
 *
 * \section COPYRIGHT
 *
 * Copyright 2012-2014 Andre Puschmann <andre.puschmann@tu-ilmenau.de>
 *
 * \section LICENSE
 *
 * This file is part of the OSPECORR Project.
 *
 * OSPECORR is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as
 * published by the Free Software Foundation, either version 3 of
 * the License, or (at your option) any later version.
 *
 * OSPECORR is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * A copy of the GNU General Public License can be found in
 * the LICENSE file in the top-level directory of this distribution
 * and at http://www.gnu.org/licenses/.
 *
 * \section DESCRIPTION
 *
 * This Class provides helper methods to access OSPECORR related function.
 *
 */

#ifndef OSPECORRHELPER_H
#define OSPECORRHELPER_H

#include <boost/format.hpp>
#include "radioconfig.pb.h"

class OspecorrHelper
{
public:
    /**
     * \brief Reconfigure single radio parameter.
     *
     * This function simply reconfigures a single parameter of the SDR in use.
     * The engine that holds the component as well as the component name, the
     * parameter name and the new parameter value need to be provided.
     * 
     * \param enginename The name of the engine 
     * \param componentname The name of the component 
     * \param parametername Which parameter
     * \param parametervalue The new value
     * \return 0 - if successful, -1 otherwise.
     */
    static int reconfigureRadioParameter(const std::string enginename, 
                                          const std::string componentname,
                                          const std::string parametername,
                                          const std::string parametervalue)
    {
        GateFactory &myFactory = GateFactory::getInstance();
        sclGate* gate = myFactory.createGate("RadioConfigClient", "control");
        
        scl_radioconfig::RadioConfigControl message = scl_radioconfig::RadioConfigControl();
        message.set_type(scl_radioconfig::REQUEST);
        message.set_command(scl_radioconfig::SET_RADIO_CONFIG);
        scl_radioconfig::RadioConfig* config = message.mutable_radioconf();
        scl_radioconfig::RadioEngine* engine = config->add_engines();
        engine->set_name(enginename);
        scl_radioconfig::RadioComponent* component = engine->add_components();
        component->set_name(componentname);
        scl_radioconfig::ComponentParameter *parameter = component->add_parameters();
        parameter->set_name(parametername);
        parameter->set_value(parametervalue);
        //std::cout << "Sending request ..." << std::endl;
        int ret = gate->sendProto(message); // send request 
        //std::cout << "Waiting for reply ..." << std::endl;
        ret = gate->recvProto(message); // receive reply
        //std::cout << "Reply received." << std::endl;
        return ret;
    }
};

#endif // OSPECORRHELPER_H
