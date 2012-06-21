/**
 * \file drmhelper.h
 *
 * This file provides static to access common functions provided by the
 * DRM such as getting a map of the available channels.
 *
 */

#ifndef DRMHELPER_H
#define DRMHELPER_H

#include "sclhelper.hpp"
#include "drm.pb.h"

typedef std::vector<scl_drm::channelSpec> ChannelMap;
typedef std::vector<scl_drm::channelSpec>::iterator ChannelMapIt;

class DrmHelper
{
    public:
        static ChannelMap getChannelMap(void)
        {
            GateFactory &myFactory = GateFactory::getInstance();
            sclGate *controlGate = myFactory.createGate("drmgenerator", "control");
            
            scl_drm::control request, reply;

            // create control packet to request channel specification
            cout << "Send GET_CHANNEL_LIST request" << endl;
            request.set_type(scl_drm::REQUEST);
            request.set_command(scl_drm::GET_CHANNEL_LIST);
            controlGate->sendProto(request);

            // wait for answer from DRM
            cout << "Wait for reply .." << endl;
            controlGate->recvProto(reply);
            assert(reply.type() == scl_drm::REPLY);
            cout << "Got reply:" << endl;
            cout << "Number of channels is: " << reply.channelmap_size() << endl;
            
            // convert DRM reply to channelmap object
            ChannelMap drmChannelMap;
            for (int i = 0; i < reply.channelmap_size(); i++) {
                drmChannelMap.push_back(reply.channelmap(i));
            }
            return drmChannelMap;
        };
};

#endif // DRMHELPER_H
