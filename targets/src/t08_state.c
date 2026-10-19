#include <stdio.h>
#include <string.h>
/* commands must arrive in order: open, auth, data, close. Any other order exits with code 3. data may repeat. */
int main(int argc, char **argv) {
    int state = 0;
    for (int i = 1; i < argc; i++) {
        const char *c = argv[i];
        if (state == 0 && !strcmp(c, "open")) state = 1;
        else if (state == 1 && !strcmp(c, "auth")) state = 2;
        else if (state == 2 && !strcmp(c, "data")) state = 2;
        else if (state == 2 && !strcmp(c, "close")) state = 3;
        else { printf("bad command %s\n", c); return 3; }
    }
    puts(state == 3 ? "session complete" : "session incomplete");
    return 0;
}
