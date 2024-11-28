#include <iostream>
#include <cstring>
#include <netinet/in.h>
#include <chrono>

//#include "comm_handler.h"

// Function to convert network byte order float to host byte order
float ntohf(uint32_t net) {
    uint32_t host = ntohl(net);
    return *reinterpret_cast<float*>(&host);
}

void unpack_pos_data(char *buf) {
    // Unpack prefix
    uint8_t prefix = buf[0];

    // Unpack size
    uint32_t size;
    std::memcpy(&size, buf + 1, sizeof(size));
    size = ntohl(size);

    // Unpack x coordinate
    uint32_t x_net;
    std::memcpy(&x_net, buf + 5, sizeof(x_net));
    float x = ntohf(x_net);

    // Unpack y coordinate
    uint32_t y_net;
    std::memcpy(&y_net, buf + 9, sizeof(y_net));
    float y = ntohf(y_net);

    // Print the unpacked data
    std::cout << "joystick position message received!" << std::endl;
    std::cout << "Prefix: " << static_cast<int>(prefix) << std::endl;
    std::cout << "Size: " << size << std::endl;
    std::cout << "X: " << x << std::endl;
    std::cout << "Y: " << y << std::endl;
}

void unpack_motctrl_data(char *buf) {
    // Unpack prefix
    uint8_t prefix = buf[0];

    // Unpack size
    uint32_t size;
    std::memcpy(&size, buf + 1, sizeof(size));
    size = ntohl(size);

    // Unpack x coordinate
    uint8_t action;
    std::memcpy(&action, buf + 5, sizeof(action));
    bool doit = action;

    // Print the unpacked data
    std::cout << "motctrl message received!" << std::endl;
    std::cout << "Prefix: " << static_cast<int>(prefix) << std::endl;
    std::cout << "Size: " << size << std::endl;
    std::cout << "Run motor? : " << (doit ? "True":"False") << std::endl;
}

void unpack_sdo_upload(char *buf) {
    // Unpack prefix
    uint8_t prefix = buf[0];

    // Unpack size
    uint32_t size;
    std::memcpy(&size, buf + 1, sizeof(size));
    size = ntohl(size);

    // Unpack node
    uint32_t node;
    std::memcpy(&node, buf + 5, sizeof(node));
    node = ntohl(node);

    // unpack index
    uint32_t idx;
    std::memcpy(&idx, buf + 9, sizeof(idx));
    idx = ntohl(idx);

    // unpack sub-index
    uint32_t subidx;
    std::memcpy(&subidx, buf + 13, sizeof(subidx));
    subidx = ntohl(subidx);

    // unpack index
    uint32_t dtype;
    std::memcpy(&dtype, buf + 17, sizeof(dtype));
    dtype = ntohl(dtype);

    // Print the unpacked data
    std::cout << "sdo-upload message received!" << std::endl;
    std::cout << "Prefix: " << static_cast<int>(prefix) << std::endl;
    std::cout << "Size: " << size << std::endl;
    std::cout << "MotorNr: " << node << std::endl;
    std::cout << std::hex << std::uppercase << std::showbase << "Index: " << idx << std::endl;
    std::cout << "Sub-Index: " << subidx << std::endl;

    // Reset to default format (decimal)
    std::cout << std::dec;  // Switch back to decimal
    std::cout << std::nouppercase;  // Reset uppercase flag
    std::cout << std::noshowbase;  // Reset showbase flag

    std::cout << "Data-Type: " << dtype << std::endl;
}
