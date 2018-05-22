all:obj/main obj/patch.so

obj/main:main.c
	mkdir -p obj
	gcc main.c -O2 -ltfix -o obj/main

obj/patch.so:patch.c
	mkdir -p obj
	gcc patch.c -c -O2 -fPIC -o obj/patch.o
	ld obj/patch.o -shared -fno-plt --defsym global_data=0xc0ffee --defsym print_global=0xc0ffee -o obj/patch.so

.PHONY: clean

clean:
	rm -rf obj/*