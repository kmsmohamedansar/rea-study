#include <stdio.h>
#include <string.h>
#include "sha256.h"
int main(int argc, char **argv) {
    if (argc < 2) { puts("usage: p06 TEXT"); return 2; }
    SHA256_CTX c; BYTE d[SHA256_BLOCK_SIZE];
    sha256_init(&c);
    sha256_update(&c, (const BYTE *)argv[1], strlen(argv[1]));
    sha256_final(&c, d);
    for (int i = 0; i < SHA256_BLOCK_SIZE; i++) printf("%02x", d[i]);
    putchar('\n');
    return 0;
}
