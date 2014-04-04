
.PHONY:		clean

CC = gcc
CXX = g++
CFLAGS = -g -O3
CXXFLAGS = $(CFLAGS) -std=c++11
LDFLAGS =
LIBS	:= -lm -lpthread

C_T	:= cqsort
CPP_T	:= qsort qsort-m qsort-m2
J_T	:= #qsort

TARGET  := $(patsubst %,o/%,$(C_T)) \
	   $(patsubst %,o/%,$(CPP_T))\
	   $(patsubst %,o/%.class,$(J_T))
	   

ALL: prebuild $(TARGET)
	@echo done 

macro:
	@echo dump macros
	@echo $(TARGET)

o/%: o/%.o
	$(CXX) -o $@ $(CXXFLAGS) $? $(LDFLAGS) $(LIBS)

o/cqsort: cqsort.c
	$(CC) -o $@ $(CFLAGS) $? $(LDFLAGS)

qsort.class: qsort.java
	javac -d o qsort.java

prebuild:
	@if [ ! -d o ]; then mkdir -p o; fi

clean:
	@rm -rf o

o/%.o: %.cpp
	$(CXX) -c $(CXXFLAGS) -o $@ $<

o/%.o: %.c
	$(CC) -c $(CFLAGS) -o $@ $<

