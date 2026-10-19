#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* An embedded blob is decrypted by XOR with the text of the environment variable QS_KEY
   (used again from the start when the blob is longer than the key) and printed.
   The key is NOT in this file or the binary. Without QS_KEY, or with an empty one, it prints
   "set QS_KEY" and exits 2. The blob is 32 bytes. */
static const unsigned char blob[] = {0x06,0x52,0x34,0x04,0x5b,0x16,0x31,0x44,0x54,0x23,0x1b,0x3f,0x0f,0x17,0x25,0x1f,0x12,0x49,0x63,0x5e,0x0a,0x7c,0x4d,0x33,0x05,0x17,0x23,0x1f,0x5d,0x15,0x76,0x50};
int main(void) {
    const char *k = getenv("QS_KEY");
    if (!k || !*k) { puts("set QS_KEY"); return 2; }
    size_t kl = strlen(k);
    for (size_t i = 0; i < sizeof blob; i++) putchar(blob[i] ^ k[i % kl]);
    putchar('\n');
    return 0;
}
