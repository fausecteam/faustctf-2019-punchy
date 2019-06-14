CC?=gcc

join.so: join.o
	$(CC) $^ -shared -o $@

join.o: join.c
	$(CC) $(CFLAGS) -c -fPIC $< -o $@
