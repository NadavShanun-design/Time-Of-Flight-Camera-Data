#include "mock_star_api.h"
#include "tof_data_generator.h"
#include <algorithm>

MockStarAPI::MockStarAPI() : nextChannelId_(1) {
    // Simulate one device with 4 channels (bitmask 0b00001111)
    devices_.push_back({0, "SpaceWire Brick Mk4", 0x0F});
}

std::vector<MockDevice> MockStarAPI::getDeviceList() {
    return devices_;
}

std::string MockStarAPI::getDeviceTypeAsString(int deviceId) {
    for (const auto& dev : devices_) {
        if (dev.id == deviceId) return dev.type;
    }
    return "Unknown Device";
}

uint8_t MockStarAPI::getDeviceChannels(int deviceId) {
    for (const auto& dev : devices_) {
        if (dev.id == deviceId) return dev.channelMask;
    }
    return 0;
}

int MockStarAPI::openChannelToLocalDevice(int deviceId, uint8_t channelNumber) {
    // Check if device exists and channel is available
    for (const auto& dev : devices_) {
        if (dev.id == deviceId && (dev.channelMask & (1 << channelNumber))) {
            // Create and store channel
            int channelId = nextChannelId_++;
            channels_.push_back({channelId, deviceId, channelNumber, true});
            return channelId;
        }
    }
    return -1;
}

void MockStarAPI::closeChannel(int channelId) {
    for (auto& ch : channels_) {
        if (ch.id == channelId) {
            ch.open = false;
            break;
        }
    }
}

void MockStarAPI::transmitPacket(int channelId, const std::vector<uint8_t>& data) {
    // For simulation, just print the data size
    printf("[MockStarAPI] Transmit on channel %d: %zu bytes\n", channelId, data.size());
}

std::vector<uint8_t> MockStarAPI::receivePacket(int channelId, size_t length) {
    if (tofGen_) {
        // Return a chunk of the first frame, starting at offset 0
        size_t numPixels = length / 2;
        return tofGen_->getFramePacket(0, 0, numPixels);
    }
    // Return a vector of incrementing values for demonstration
    std::vector<uint8_t> data(length);
    for (size_t i = 0; i < length; ++i) data[i] = static_cast<uint8_t>(i & 0xFF);
    printf("[MockStarAPI] Receive on channel %d: %zu bytes\n", channelId, length);
    return data;
}

void MockStarAPI::setToFDataGenerator(ToFDataGenerator* gen) {
    tofGen_ = gen;
} 