#include <stdio.h>
#include <string.h>
#include <stdlib.h>
/* normal run prints a greeting. A hidden switch, the environment variable QS_DIAG set to "7", prints diagnostics. */
int main(int argc, char **argv) {
    const char *d = getenv("QS_DIAG");
    puts("hello from t04");
    if (d && strcmp(d, "7") == 0) {
        printf("diag: argc=%d pid-independent build=2026\n", argc);
    }
    return 0;
}
