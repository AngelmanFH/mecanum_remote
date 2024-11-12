#include <iostream>
#include <vector>
#include <cstring>
#include <arpa/inet.h>  // For ntohl and ntohf

// Function to convert network byte order float to host byte order
float ntohf(uint32_t net) {
    uint32_t host = ntohl(net);
    return *reinterpret_cast<float*>(&host);
}

void unpack_data(const std::vector<uint8_t>& buffer) {
    if (buffer.size() < 13) {
        std::cerr << "Buffer too small" << std::endl;
        return;
    }

    // Unpack prefix
    uint8_t prefix = buffer[0];

    // Unpack size
    uint32_t size;
    std::memcpy(&size, buffer.data() + 1, sizeof(size));
    size = ntohl(size);

    // Unpack x coordinate
    uint32_t x_net;
    std::memcpy(&x_net, buffer.data() + 5, sizeof(x_net));
    float x = ntohf(x_net);

    // Unpack y coordinate
    uint32_t y_net;
    std::memcpy(&y_net, buffer.data() + 9, sizeof(y_net));
    float y = ntohf(y_net);

    // Print the unpacked data
    std::cout << "Prefix: " << static_cast<int>(prefix) << std::endl;
    std::cout << "Size: " << size << std::endl;
    std::cout << "X: " << x << std::endl;
    std::cout << "Y: " << y << std::endl;
}

int main() {
    // Example buffer received from TCP link
    std::vector<uint8_t> buffer = {0x01, 0x00, 0x00, 0x00, 0x08, 0x41, 0x20, 0x00, 0x00, 0x41, 0xA0, 0x00, 0x00};

    // Unpack the data
    unpack_data(buffer);

    return 0;
}
