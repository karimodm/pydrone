CC=gcc
PYTHONDIR=../../../../Python25
CFLAGS=-s -Os -I ${PYTHONDIR}/include -L ${PYTHONDIR}/libs
LIBS=-lpython25

all: evocate.o
	${CC} ${CFLAGS} evocate.o -oevocate ${LIBS}
	
clean:
	rm -f evocate evocate.o evocate.exe *.pyc IP.txt 
	