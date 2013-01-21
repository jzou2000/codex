CC = gcc
CXX = g++
CFLAGS = -Wall `pkg-config --cflags gtk+-2.0`
LDFLAGS = `pkg-config --libs gtk+-2.0`


o/bt: bt.o
	$(CC) -rdynamic -o $@ $(CFLAGS) $? $(LDFLAGS)

o/glib: glib.o
	$(CC) -o $@ $(CFLAGS) $? $(LDFLAGS)


.c.o:
	$(CC) -o $@ -c $(CFLAGS) $<
