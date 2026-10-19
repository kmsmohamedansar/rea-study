#include <stdio.h>
#include <string.h>
/* checks a password by hashing it with djb2 and comparing to a stored constant. The password is "quill42". */
static unsigned long djb2(const char *s) {
    unsigned long h = 5381;
    int c;
    while ((c = (unsigned char)*s++)) h = ((h << 5) + h) + c;
    return h & 0xffffffffUL;
}
int main(int argc, char **argv) {
    if (argc < 2) { puts("usage: t07 PASSWORD"); return 2; }
    if (djb2(argv[1]) == DJB2_EXPECTED) { puts("access granted"); return 0; }
    puts("access denied");
    return 1;
}
