#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* An embedded blob is decrypted with a key derived from the environment variable QS_USER:
   h = djb2 of the text of QS_USER (start 5381, h = h*33 + c, 32 bits). Blob byte i is XORed with
   the byte (h >> (8 * (i % 4))) & 0xff, and the result is printed. The right user name is NOT in
   this file or the binary. Without QS_USER (or with an empty one) it prints "set QS_USER" and
   exits 2. The blob is 42 bytes. */
static const unsigned char blob[] = {0x3a,0xe6,0x89,0xf8,0x2d,0xf7,0xca,0xe1,0x2d,0xe9,0x99,0xb3,0x36,0xee,0x8d,0xfb,0x2c,0xeb,0x93,0xb3,0x39,0xf3,0xca,0xa3,0x6a,0xbd,0xda,0xa3,0x78,0xf3,0x85,0xb3,0x3a,0xf2,0x89,0xf8,0x3d,0xf3,0xca,0xf1,0x75,0xb0};
int main(void) {
    const char *u = getenv("QS_USER");
    if (!u || !*u) { puts("set QS_USER"); return 2; }
    unsigned h = 5381;
    for (const char *p = u; *p; p++) h = h * 33 + (unsigned char)*p;
    for (size_t i = 0; i < sizeof blob; i++) putchar(blob[i] ^ ((h >> (8 * (i % 4))) & 0xff));
    putchar('\n');
    return 0;
}
