#include <string.h>
#include <stdio.h>
#include <stdlib.h>

char* join_commands (char** lines, int len) {
  size_t l = 1;

  for (int i = 0; i < len; i++) {
      l += strlen(lines[i]) + 1;
  }

	char* res = calloc(l, 1);
  if (!res) {
			perror("calloc");
			return NULL;
  }

  for (int i = 0; i < len; i++) {
		strcat(res, lines[i]);

		if (i == len - 1) {
			res[strlen(res)] = '\0';
		} else {
			res[strlen(res)] = '\n';
		}
	}

	return res;
}

void free_memory (void* mem) {
	free(mem);
}

#if MAIN
void main (int argc, char** argv) {
	if (argc <= 1) {
		fprintf(stderr, "lolnope\n");
		exit(1);
	}

	char* list = join_commands(&argv[1], argc - 1);
	printf("%s", list);
	free_memory(list);
	exit(0);
}
#endif
