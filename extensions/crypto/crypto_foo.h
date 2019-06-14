#include <stddef.h>
#include <stdio.h>

unsigned char* read_file(const char* filename, size_t* f_len);
void encrypt(const char* filename, FILE* out);
char* decrypt(const char* filename);
