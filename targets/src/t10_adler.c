#include <stdio.h>
#include <string.h>
/* prints the Adler-32 checksum of argv[1] as 8 hex digits (modulus 65521). */
int main(int argc, char **argv) {
    if (argc < 2) return 2;
    unsigned a = 1, b = 0;
    for (const unsigned char *p = (const unsigned char *)argv[1]; *p; p++) {
        a = (a + *p) % 65521;
        b = (b + a) % 65521;
    }
    printf("%08x\n", (b << 16) | a);
    return 0;
}
