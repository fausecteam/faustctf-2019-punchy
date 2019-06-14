all: libstaply.so staply

libstaply.so: staply.c
	gcc -shared -fPIC -o $@ $< ../crypto/libcrypto_foo.a -lcrypto

staply: staply.c
	gcc -DMAIN -o $@ $< ../crypto/libcrypto_foo.a -lcrypto
