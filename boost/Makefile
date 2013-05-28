CXX = g++
CXXFLAGS = $(CFLAGS) -std=c++11

boost-regex: boost-regex.o
	$(CXX) -o $@ $? -lboost_regex

.cpp.o:
	$(CXX) $(CXXFLAGS) -c -o $@ $?
