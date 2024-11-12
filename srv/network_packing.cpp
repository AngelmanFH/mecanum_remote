#include <iostream>
#include <cstring>  // For std::memcpy
#include <arpa/inet.h>  // For ntohl

int main() {
    // Example packed data (received from the network)
    unsigned char packed_data[] = {0x00, 0x00, 0x00, 0x2A, 0x40, 0x48, 0xF5, 0xC3};

    // Variables to hold the unpacked data
    int int_value;
    float float_value;

    // Unpack the integer (network byte order to host byte order)
    std::memcpy(&int_value, packed_data, sizeof(int));
    int_value = ntohl(int_value);  // Convert from network byte order to host byte order

    // Unpack the float (network byte order to host byte order)
    uint32_t float_as_int;
    std::memcpy(&float_as_int, packed_data + sizeof(int), sizeof(float_as_int));
    float_as_int = ntohl(float_as_int);  // Convert from network byte order to host byte order
    std::memcpy(&float_value, &float_as_int, sizeof(float_value));

    // Output the unpacked values
    std::cout << "Unpacked int: " << int_value << std::endl;
    std::cout << "Unpacked float: " << float_value << std::endl;

    return 0;
}

