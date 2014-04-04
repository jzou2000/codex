
.PHONY:		clean

CC = gcc
CXX = g++
CFLAGS = -g -O3
CXXFLAGS = $(CFLAGS) -std=c++11
LDFLAGS =
LIBS	:= -lm -lpthread


TARGET  := o/cqsort o/qsort o/qsort-m #qsort.class

ALL: prebuild $(TARGET)
	@echo done

o/cqsort: cqsort.c
	$(CC) -o $@ $(CFLAGS) $? $(LDFLAGS)

o/qsort: o/qsort.o
	$(CXX) -o $@ $(CXXFLAGS) $? $(LDFLAGS)

o/qsort-m: o/qsort-m.o
	$(CXX) -o $@ $(CXXFLAGS) $? $(LDFLAGS)

prebuild:
	@if [ ! -d o ]; then mkdir -p o; fi

clean:
	@rm -rf o

o/%.o: %.cpp
	$(CXX) -c $(CXXFLAGS) -o $@ $<

o/%.o: %.c
	$(CC) -c $(CFLAGS) -o $@ $<

