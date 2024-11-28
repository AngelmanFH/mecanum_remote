# Define the compiler
CXX = g++

# Define the target executable
TARGET = server

# Define the source files
SRCS = main.cpp comm_handler.cpp

# Define the object files
OBJS = $(SRCS:.cpp=.o)

# Define the compiler flags
CXXFLAGS = -Wall -g

# Default target
all: $(TARGET)

# Rule to build the target executable
$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS)

# Rule to build the object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Rule to clean the build directory
clean:
	rm -f $(OBJS) $(TARGET)

# Phony targets
.PHONY: all clean
