all: libcrypto_foo.a crypto

libcrypto_foo.a: crypto_foo.o
	rm -f $@ || true
	ar rcs $@ $<

crypto_foo.o: crypto_foo.c
	gcc -fPIC -c $< -o $@ -lcrypto

crypto: crypto_foo.c
	gcc -DMAIN  $< -o $@ -lcrypto
