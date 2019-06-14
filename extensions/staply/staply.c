#include "../crypto/crypto_foo.h"
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

char* staply_source;

char* check_for_possible_help(char* data) {
    char* pos = strstr(data, "IDENTIFICATION DIVISION.");
    if (pos == NULL) {
        return NULL;
    } else {
        return staply_source;
    }
}

char* run_help(char* code) {
    char template[] = "data/punchXXXXXX.cob";
    char* path = strdup(template);
    char templateout[] = "data/punchXXXXXX";
    char* pathout = strdup(templateout);

    int fd = mkstemps(path, 4);
    int fdout = mkstemps(pathout, 0);
    close(fdout);

    char* data = strdup("Error.");

    FILE* f = fdopen(fd, "w");
    fwrite(code, strlen(code), 1, f);
    fwrite("\n", 1, 1, f);
    fflush(f);
    fclose(f);

    char* ex_path = pathout;

    char command1[] = "cobc -x ";
    char commandout[] = " -o ";
    char* cmdline = calloc(sizeof(template) + sizeof(templateout) + sizeof(command1) + sizeof(commandout) + 1, 1);
    strcpy(cmdline, command1);
    strcat(cmdline, path);
    strcat(cmdline, commandout);
    strcat(cmdline, pathout);

    int ret = system(cmdline);
    free(cmdline);

    if (ret != 0) {
        goto out1;
    }

    char command2[] = "timeout 0.5 ./";
    cmdline = calloc(sizeof(template) + sizeof(command2) + 1, 1);
    strcpy(cmdline, command2);
    strcat(cmdline, ex_path);
    FILE* stream = popen(cmdline, "r");
    free(cmdline);

    if (stream == NULL) {
        perror("");
        goto out1;
    }

    sleep(1);

    free(data);
    data = calloc(4096, 1);
    fread(data, 4095, 1, stream);
    pclose(stream);

 out1:
    unlink(path);
    free(path);
    unlink(ex_path);
    free(ex_path);

    return data;
}

void init_staply() {
    staply_source = decrypt("staply.enc");
}

#ifdef MAIN
int main() {
    init_staply();
    run_help("IDENTIFICATION SECTION. PROGRAM-ID foo.");
}
#endif
