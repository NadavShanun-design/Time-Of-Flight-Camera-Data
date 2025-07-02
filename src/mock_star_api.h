#pragma once
#include <string>
#include <vector>
#include <cstdint>

class ToFDataGenerator; // Forward declaration

// Simulated device/channel/packet structures
struct MockDevice {
    int id;
    std::string type;
    uint8_t channelMask; // bitmask for available channels
};

struct MockChannel {
    int id;
    int deviceId;
    uint8_t channelNumber;
    bool open;
};

class MockStarAPI {
public:
    MockStarAPI();
    // Returns a list of available devices (simulated)
    std::vector<MockDevice> getDeviceList();
    // Returns the type string for a device
    std::string getDeviceTypeAsString(int deviceId);
    // Returns the channel bitmask for a device
    uint8_t getDeviceChannels(int deviceId);
    // Opens a channel to a device, returns channel id or -1 on failure
    int openChannelToLocalDevice(int deviceId, uint8_t channelNumber);
    // Closes a channel
    void closeChannel(int channelId);
    // Simulates transmitting a packet (stores or logs data)
    void transmitPacket(int channelId, const std::vector<uint8_t>& data);
    // Simulates receiving a packet (returns mock data or ToF data if generator is set)
    std::vector<uint8_t> receivePacket(int channelId, size_t length);
    // Set a ToFDataGenerator to use for receivePacket
    void setToFDataGenerator(ToFDataGenerator* gen);
private:
    std::vector<MockDevice> devices_;
    std::vector<MockChannel> channels_;
    int nextChannelId_;
    ToFDataGenerator* tofGen_ = nullptr;
}; 