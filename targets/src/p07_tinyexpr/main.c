#include <stdio.h>
#include "tinyexpr.h"
int main(int argc, char **argv) {
    if (argc < 2) { puts("usage: p07 EXPR"); return 2; }
    int err;
    double v = te_interp(argv[1], &err);
    if (err) { printf("error at position %d\n", err); return 1; }
    printf("%g\n", v);
    return 0;
}
