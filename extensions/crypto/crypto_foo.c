#include <stdio.h>
#include <stdlib.h>
#include <openssl/evp.h>

unsigned char *key = (unsigned char *)"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
unsigned char *iv =  (unsigned char *)"bbbbbbbbbbbbbbbb";

unsigned char* read_file(const char* filename, size_t* f_len) {
    FILE* f = fopen(filename, "r");
    fseek(f,0L,SEEK_END);
    *f_len = ftell(f);
    fseek(f,0L,SEEK_SET);

    unsigned char* text = (unsigned char*)calloc(*f_len + 1, 1);
    fread(text, *f_len, 1, f);
    fclose(f);

    return text;
}

void encrypt(const char* filename, FILE* out) {
    size_t f_len;
    unsigned char* plaintext = read_file(filename, &f_len);
    f_len++;
    unsigned char* encrypted = calloc(f_len + 513, 1);

    EVP_CIPHER_CTX *ctx;
    ctx = EVP_CIPHER_CTX_new();

    int complete_len = 0;
    int len = 0;
    EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, key, iv);
    EVP_EncryptUpdate(ctx, encrypted, &len, plaintext, f_len);
    complete_len += len;
    EVP_EncryptFinal_ex(ctx, encrypted + len, &len);
    complete_len += len;

    EVP_CIPHER_CTX_free(ctx);
    fwrite(encrypted, complete_len, 1, out);
    fflush(out);
}

char* decrypt(const char* filename) {
    size_t f_len;
    unsigned char* ciphertext = read_file(filename, &f_len);
    unsigned char* plaintext = calloc(f_len + 1, 1);

    EVP_CIPHER_CTX *ctx;
    ctx = EVP_CIPHER_CTX_new();

    int complete_len = 0;
    int len = 0;
    EVP_DecryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, key, iv);
    EVP_DecryptUpdate(ctx, plaintext, &len, ciphertext, f_len);
    complete_len += len;
    EVP_DecryptFinal_ex(ctx, plaintext + complete_len, &len);
    complete_len += len;

    EVP_CIPHER_CTX_free(ctx);

    return plaintext;
}

#ifdef MAIN
int main(int argc, char** argv) {
    encrypt(argv[1], stdout);
}
#endif
