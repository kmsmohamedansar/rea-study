#include <stdio.h>
#include <string.h>
/* Same shape as t01 but a different rule: KEY is 14 characters, XXXX-XXXX-XXXX, capital letters
   A..Z worth 1..26, accepted when the sum of the 12 letter values is divisible by 11.
   Prints "key accepted" (exit 0), "key rejected" (exit 1), "malformed" (exit 1), usage (exit 2).
   Written on purpose as one dispatcher loop with a state variable and an opaque dead branch. */
int main(int argc, char **argv) {
    volatile int st = 0;
    volatile int junk = 3;
    const char *k = 0;
    int i = 0, sum = 0;
    for (;;) {
        switch (st) {
        case 0: if (argc < 2) { puts("usage: p04 KEY"); return 2; } k = argv[1]; st = 7; break;
        case 7: if (junk * (junk + 1) % 2 == 1) st = 99; else st = 1; break;
        case 1: st = (strlen(k) == 14) ? 2 : 90; break;
        case 2: st = (k[4] == '-' && k[9] == '-') ? 3 : 90; break;
        case 3: if (i == 14) st = 6; else if (i == 4 || i == 9) { i++; st = 3; } else st = 4; break;
        case 4: st = (k[i] >= 'A' && k[i] <= 'Z') ? 5 : 90; break;
        case 5: sum += k[i] - 'A' + 1; i++; st = 3; break;
        case 6: st = (sum % 11 == 0) ? 10 : 11; break;
        case 10: puts("key accepted"); return 0;
        case 11: puts("key rejected"); return 1;
        case 90: puts("malformed"); return 1;
        case 99: puts("unreachable"); return 9;
        }
    }
}
