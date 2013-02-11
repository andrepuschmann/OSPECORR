/**
 * \file drmhelper.h
 *
 * This file provides static to access common functions provided by the
 * DRM such as getting a map of the available channels.
 *
 */

#ifndef DRMHELPER_H
#define DRMHELPER_H

#include "boost/date_time/posix_time/posix_time.hpp"
#include "sclhelper.hpp"
#include "drm.pb.h"
#include "phy.pb.h"

typedef std::vector<scl_drm::channelSpec> ChannelMap;
typedef std::vector<scl_drm::channelSpec>::iterator ChannelMapIt;
typedef std::vector<scl_drm::channelSpec>::const_iterator ChannelMapConstIt;

typedef std::vector<scl_phy::BasicChannel> BasicChannelMap;
typedef std::vector<scl_phy::BasicChannel>::const_iterator BasicChannelMapConstIt;

//! Exception which can be thrown by DRM helper class
class DrmHelperException : public std::exception
{
private:
    std::string d_message;
public:
    DrmHelperException(const std::string &message) throw()
        :exception(), d_message(message)
    {};
    virtual const char* what() const throw()
    {
        return d_message.c_str();
    };
    virtual ~DrmHelperException() throw()
    {};
};

class DrmHelper
{
    public:
        static ChannelMap getChannelMap(void)
        {
            GateFactory &myFactory = GateFactory::getInstance();
            sclGate *controlGate = myFactory.createGate("drmclient", "control");
            
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
        }

        static BasicChannelMap getBasicChannelMap(void)
        {
            ChannelMap drmMap = DrmHelper::getChannelMap();
            BasicChannelMap basicMap;

            for (ChannelMapIt it = drmMap.begin(); it != drmMap.end(); it++) {
                basicMap.push_back(DrmHelper::convertToBasicChannel(*it));
            }
        }


        static ChannelMap removeChannelFromMap(const scl_drm::channelSpec channel, const ChannelMap oldMap)
        {
            // find channel in newmap and remove it, note that we have to compare element by element
            // because ==operator is not defined for protobuf messages
            ChannelMap map = oldMap;
            for (ChannelMapIt it = map.begin(); it != map.end(); ++it) {
                if (it->f_center() == channel.f_center() && it->bandwidth() == channel.bandwidth()) {
                    map.erase(it);
                }
            }
            return map;
        }

        static scl_drm::channelSpec getChannel(const scl_drm::channelProp property)
        {
            GateFactory &myFactory = GateFactory::getInstance();
            sclGate *controlGate = myFactory.createGate("drmclient", "control");

            scl_drm::control request, reply;

            // create control packet to request channel specification
            cout << "Send GET_SINGLE_CHANNEL request" << endl;
            request.set_type(scl_drm::REQUEST);
            request.set_command(scl_drm::GET_SINGLE_CHANNEL);
            request.set_prop(property);
            controlGate->sendProto(request);

            // wait for answer from DRM
            cout << "Wait for reply .." << endl;
            controlGate->recvProto(reply);
            assert(reply.type() == scl_drm::REPLY);
            cout << "Got reply:" << endl;
            if (reply.channelmap_size() == 0)
                throw DrmHelperException("DRM did not send a proper channel configuration.");
            return reply.channelmap(0);
        }


        static void updateChannelState(const scl_drm::statusUpdate update)
        {
            GateFactory &myFactory = GateFactory::getInstance();
            sclGate *dataGate = myFactory.createGate("drmclient", "data");
            dataGate->sendProto(update);
        }


        static scl_phy::BasicChannel convertToBasicChannel(const scl_drm::channelSpec drmChannel)
        {
            scl_phy::BasicChannel basicChannel;
            basicChannel.set_f_center(drmChannel.f_center());
            basicChannel.set_bandwidth(drmChannel.bandwidth());
            return basicChannel;
        }


        static scl_drm::channelSpec convertToDrmChannel(const scl_phy::BasicChannel basicChannel)
        {
            scl_drm::channelSpec drmChannel;
            drmChannel.set_f_center(basicChannel.f_center());
            drmChannel.set_bandwidth(basicChannel.bandwidth());
            return drmChannel;
        }

        
        static uint64_t getTimeSinceEpoch()
        {
            boost::posix_time::ptime epoch = boost::posix_time::time_from_string("1970-01-01 00:00:00.000");
            boost::posix_time::ptime other = boost::posix_time::microsec_clock::local_time();
            return (other-epoch).total_milliseconds();
        }
};

#endif // DRMHELPER_H
