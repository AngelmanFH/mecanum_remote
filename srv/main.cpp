#include <iostream>
#include <iomanip>
#include <string>
#include <cstring>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <chrono>
#include <thread>
#include <arpa/inet.h>
#include <csignal>

bool quitting;
// Signal handler function
void signalHandler(int signum) {
    std::cout << "Interrupt signal (" << signum << ") received.\n";
    // Cleanup and close up stuff here
    quitting = true;
    // Terminate program
    exit(signum);
}

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

void handle_client(int client_socket) {
    char buffer[1024];
    int count = 0;
    auto last_keep_alive = std::chrono::steady_clock::now();
    
    // Set a timeout for the recv() call
    struct timeval timeout;
    timeout.tv_sec = 1;  // 1 second timeout
    timeout.tv_usec = 0;
    setsockopt(client_socket, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    
    while (true) {
        memset(buffer, 0, sizeof(buffer));
        int bytes_received = recv(client_socket, buffer, sizeof(buffer) - 1, 0);
        if (bytes_received <= 0) {
            if (bytes_received == 0) {
                std::cerr << "Connection closed by client" << std::endl;
                break;
            } else if (errno == EWOULDBLOCK || errno == EAGAIN) {
                // Timeout occurred, check if the last keep-alive message was received within the last second
                auto now = std::chrono::steady_clock::now();
                auto duration_since_last_keep_alive = std::chrono::duration_cast<std::chrono::milliseconds>(now - last_keep_alive).count();
                if (duration_since_last_keep_alive > 1000) {
                    std::cerr << "Connection lost: No keep-alive message received for over 1 second" << std::endl;
                    break;
                }
            } else {
                std::cerr << "Error occurred: " << strerror(errno) << std::endl;
                break;
            }
        } else {
            switch(buffer[0]) {
                case 0x01: unpack_pos_data(buffer);
                break;
                case 0x02: unpack_motctrl_data(buffer);
                break;
                case 0x03: unpack_sdo_upload(buffer);
                break;
                default: {
                    std::string received_message(buffer);
                    if (received_message == "KEEP_ALIVE") {
                        last_keep_alive = std::chrono::steady_clock::now();
                    } else {
                        std::cout << "Received: " << buffer << std::endl;
                    }
                }
            }

            // Increment the count and send a message to the client
            count++;
            std::string message = "Server says: Hello, GUI! Count: " + std::to_string(count);
            send(client_socket, message.c_str(), message.size(), 0);
        }
    }
    close(client_socket);
}

int main() {
    // Register signal handler for SIGINT (CTRL-C)
    signal(SIGINT, signalHandler);

    int server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket == -1) {
        std::cerr << "Failed to create socket" << std::endl;
        return 1;
    }
    
    // Set the socket option to reuse the address
    int opt = 1;
    if (setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) == -1) {
        std::cerr << "Failed to set socket options" << std::endl;
        close(server_socket);
        return 1;
    }

    sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(54000);
    server_addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(server_socket, (sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        std::cerr << "Failed to bind to port" << std::endl;
        close(server_socket);
        return 1;
    }

    if (listen(server_socket, SOMAXCONN) == -1) {
        std::cerr << "Failed to listen on socket" << std::endl;
        close(server_socket);
        return 1;
    }

    while(true) {
        std::cout << "Server is listening on port 54000" << std::endl;

        sockaddr_in client_addr;
        socklen_t client_size = sizeof(client_addr);
        int client_socket = accept(server_socket, (sockaddr *) &client_addr, &client_size);
        if (client_socket == -1) {
            std::cerr << "Failed to accept connection" << std::endl;
            close(server_socket);
            return 1;
        }
        char client_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, INET_ADDRSTRLEN);

        std::cout << "accepted connection from " << client_ip << " on port " << ntohs(client_addr.sin_port)
                  << std::endl;

        handle_client(client_socket);
    }
    close(server_socket);
    return 0;
}

