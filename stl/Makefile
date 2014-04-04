
.PHONY:		clean

CC = gcc
CXX = g++
CFLAGS = -g -O3
CXXFLAGS = $(CFLAGS) -std=c++11
LDFLAGS =

LIBS	:= -lm -lpthread

CPP_T	:=
STL_T	:= re copy lambda cast \
           async async2 mt-pc
BOOST_T	:= regex lambda

TARGET  := $(patsubst %,o/cpp-%,$(CPP_T)) \
	   $(patsubst %,o/stl-%,$(STL_T)) \
	   $(patsubst %,o/boost-%,$(BOOST_T))

SRC     := $(patsubst %,%.cpp,$(TARGET))
EXE     := $(patsubst %,o/%,$(TARGET))
OBJ     := $(patsubst %,obj/%.o,$(TARGET))

ALL: prebuild $(TARGET)
	@echo done

macro:
	@echo dump macros
	@echo $(TARGET)

prebuild:
	@if [ ! -d o ]; then mkdir -p o; fi

o/boost-regex: boost-regex.cpp
	$(CXX) -o $@ $(CXXFLAGS) $? $(LDFLAGS) -lboost_regex

clean:
	rm -rf o

o/%: o/%.o
	$(CXX) -o $@ $(CXXFLAGS) $? $(LDFLAGS) $(LIBS)

o/%.o: %.cpp
	$(CXX) -c $(CXXFLAGS) -o $@ $<

o/%.o: %.c
	$(CC) -c $(CFLAGS) -o $@ $<

