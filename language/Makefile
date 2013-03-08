
CXX = g++
CXXFLAGS = -g
LDFLAGS =

cpp_contain: cpp_contain.o
	$(CXX) -o $@ $? $(LDFLAGS)

qsort: qsort.o
	$(CXX) -o $@ $? $(LDFLAGS)

.cpp.o:
	$(CXX) -c $(CXXFLAGS) $<

