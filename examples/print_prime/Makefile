all:obj/patch.tfp

obj/patch.tfp:obj/main obj/patch.o
	tfix gen -m obj/main -p obj/patch.o -o obj/patch.tfp

obj/main:main.c
	mkdir -p obj
	gcc main.c -O2 -ltfix -o obj/main

obj/patch.o:patch.c
	mkdir -p obj
	gcc patch.c -c -O2 -fPIC -o obj/patch.o

.PHONY: clean

clean:
	rm -rf obj/