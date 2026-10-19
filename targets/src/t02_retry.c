#include <stdio.h>
#include <stdlib.h>
/* pretend network call that fails twice then works (argv[1] = failures before success) */
static int attempt_no = 0, fail_until = 2;
static int call(void) { return ++attempt_no > fail_until ? 0 : -1; }
int main(int argc, char **argv) {
    if (argc > 1) fail_until = atoi(argv[1]);
    int delay_ms = 200;
    for (int tries = 1; tries <= 5; tries++) {
        if (call() == 0) { printf("ok after %d tries\n", tries); return 0; }
        printf("try %d failed, wait %d ms\n", tries, delay_ms);
        delay_ms *= 2;
        if (delay_ms > 2000) delay_ms = 2000;
    }
    puts("gave up");
    return 1;
}
