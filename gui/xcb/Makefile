
.PHONY:		clean

CC = gcc
CXX = g++
CFLAGS = -g
CXXFLAGS = $(CFLAGS) -std=c++11
LDFLAGS =

LIBS	:= -lxcb -lm -lpthread

TARGET  := hello

SRC     := $(patsubst %,%.cpp,$(TARGET))
EXE     := $(patsubst %,o/%,$(TARGET))
OBJ     := $(patsubst %,obj/%.o,$(TARGET))

ALL: prebuild $(EXE)
	@echo done

macro:
	@echo dump macros
	@echo $(TARGET)

prebuild:
	@if [ ! -d o ]; then mkdir -p o; fi

clean:
	rm -rf o

o/%: o/%.o
	$(CXX) -o $@ $(CXXFLAGS) $? $(LDFLAGS) $(LIBS)

o/%.o: %.cpp
	$(CXX) -c $(CXXFLAGS) -o $@ $<

o/%.o: %.c
	$(CC) -c $(CFLAGS) -o $@ $<

