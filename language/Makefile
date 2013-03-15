
CC = gcc
CXX = g++
CFLAGS = -O3
CXXFLAGS = $(CFLAGS)
LDFLAGS =

cpp_contain: cpp_contain.o
	$(CXX) -o $@ $? $(LDFLAGS)

qsort: qsort.o
	$(CXX) -o $@ $(CXXFLAGS) $? $(LDFLAGS)

cqsort: cqsort.o
	$(CC) -o $@ $(CFLAGS) $? $(LDFLAGS)

qsort.class: qsort.java
	javac qsort.java

.cpp.o:
	$(CXX) -c $(CXXFLAGS) $<

.c.o:
	$(CC) -c $(CFLAGS) $<

