

CXX = g++
CC = gcc
GTK_CFLAGS = `pkg-config --cflags gtk+-2.0`
GTK_LDFLAGS = `pkg-config --libs gtk+-2.0`
CFLAGS = -g -Wall $(GTK_CFLAGS)
LDFLAGS = $(GTK_LDFLAGS)

o/gtkdialog: gtkdialog.c
	$(CC) -o $@ $(CFLAGS) $? $(LDFLAGS)

.c.o:
	$(CC) $(CFLAGS) -c -o $@ $<

