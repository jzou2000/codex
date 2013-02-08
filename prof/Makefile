CC = gcc
LD = gcc

CFLAGS = -g
LDFLAGS =

prof-demo: prof-demo.o
	$(CC) -o $@ $(CFLAGS) $? $(LDFLAGS)

.c.o:
	$(CC) -o $@ -c $(CFLAGS) $<  
