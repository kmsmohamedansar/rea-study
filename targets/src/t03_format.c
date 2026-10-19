#include <stdio.h>
#include <string.h>
#include <stdint.h>
/* file layout: 4 bytes "QSTK", 1 byte version (must be 2), 4 bytes payload length (little endian, max 4096), payload */
int main(int argc, char **argv) {
    if (argc < 2) { puts("usage: t03 FILE"); return 2; }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { puts("cannot open"); return 2; }
    unsigned char h[9];
    if (fread(h, 1, 9, f) != 9 || memcmp(h, "QSTK", 4) != 0) { puts("not a QSTK file"); return 1; }
    if (h[4] != 2) { puts("unsupported version"); return 1; }
    uint32_t len = h[5] | (h[6] << 8) | (h[7] << 16) | ((uint32_t)h[8] << 24);
    if (len > 4096) { puts("payload too large"); return 1; }
    printf("ok, payload %u bytes\n", len);
    fclose(f);
    return 0;
}
