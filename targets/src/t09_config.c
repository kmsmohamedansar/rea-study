#include <stdio.h>
#include <string.h>
#include <stdlib.h>
/* reads key=value lines from a file. '#' starts a comment. Only the key "timeout" matters:
   default 30, values above 300 are clamped to 300, values below 1 fall back to the default. */
int main(int argc, char **argv) {
    if (argc < 2) { puts("usage: t09 FILE"); return 2; }
    FILE *f = fopen(argv[1], "r");
    if (!f) return 2;
    char line[256]; int timeout = 30;
    while (fgets(line, sizeof line, f)) {
        char *hash = strchr(line, '#'); if (hash) *hash = 0;
        char *eq = strchr(line, '='); if (!eq) continue;
        *eq = 0;
        if (strcmp(line, "timeout") == 0) {
            int v = atoi(eq + 1);
            if (v < 1) v = 30;
            if (v > 300) v = 300;
            timeout = v;
        }
    }
    printf("timeout=%d\n", timeout);
    fclose(f);
    return 0;
}
