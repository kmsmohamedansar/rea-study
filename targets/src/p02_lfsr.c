#include <stdio.h>
/* Stream cipher. Galois LFSR, 16 bit state, seed 0xACE1, feedback mask 0xB400 (shift right,
   XOR the mask in when the bit shifted out was 1). Eight steps make one keystream byte, first
   bit out is the lowest bit. Each input byte is XORed with a keystream byte and printed as two
   lowercase hex digits. There is no key: the seed is fixed. */
int main(int argc, char **argv) {
    if (argc < 2) { puts("usage: p02 TEXT"); return 2; }
    unsigned short s = 0xACE1;
    for (const unsigned char *p = (const unsigned char *)argv[1]; *p; p++) {
        unsigned char ks = 0;
        for (int b = 0; b < 8; b++) {
            unsigned lsb = s & 1;
            s >>= 1;
            if (lsb) s ^= 0xB400;
            ks |= lsb << b;
        }
        printf("%02x", *p ^ ks);
    }
    putchar('\n');
    return 0;
}
