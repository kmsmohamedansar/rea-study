#include <stdio.h>
#include <stdlib.h>
/* allow at most 5 requests in any 60 second window. argv: timestamps in seconds, one per request. */
int main(int argc, char **argv) {
    long seen[5]; int n = 0;
    for (int i = 1; i < argc; i++) {
        long t = atol(argv[i]);
        int in_window = 0;
        for (int j = 0; j < n; j++) if (t - seen[j] < 60) in_window++;
        if (in_window >= 5) { printf("t=%ld denied\n", t); continue; }
        if (n < 5) seen[n++] = t;
        else { for (int j = 0; j < 4; j++) seen[j] = seen[j+1]; seen[4] = t; }
        printf("t=%ld allowed\n", t);
    }
    return 0;
}
