#include <stdio.h>
#include <string.h>
/* key format: 3 groups of 4 letters joined by '-', e.g. ABCD-EFGH-IJKL.
   valid when the sum of all letter values (A=1..Z=26) is divisible by 7. */
int main(int argc, char **argv) {
    if (argc < 2) { puts("usage: t01 KEY"); return 2; }
    const char *k = argv[1];
    if (strlen(k) != 14 || k[4] != '-' || k[9] != '-') { puts("bad format"); return 1; }
    int sum = 0;
    for (int i = 0; i < 14; i++) {
        if (i == 4 || i == 9) continue;
        if (k[i] < 'A' || k[i] > 'Z') { puts("bad format"); return 1; }
        sum += k[i] - 'A' + 1;
    }
    if (sum % 7 == 0) { puts("licence ok"); return 0; }
    puts("licence invalid");
    return 1;
}
