#include <stdio.h>
/* stack machine with 8 opcodes: 0 HALT, 1 PUSH n, 2 ADD, 3 SUB, 4 MUL, 5 DUP,
   6 JNZ addr (pop, jump if not zero), 7 PRINT (pop, print as a decimal line).
   The embedded program prints 720 (1*2*3*4*5*6), then counts down 3, 2, 1.
   The stack holds 32 values. An unknown opcode prints "bad opcode" and exits 1. */
static const unsigned char prog[] = {
    1,1, 1,2, 4, 1,3, 4, 1,4, 4, 1,5, 4, 1,6, 4, 7,   /* 0-17: 720 */
    1,3,                                               /* 18: PUSH 3 */
    5, 7,                                              /* 20: DUP PRINT (loop) */
    1,1, 3,                                            /* 22: PUSH 1 SUB */
    5, 6,20,                                           /* 25: DUP JNZ 20 */
    0 };
int main(void) {
    int st[32], sp = 0;
    unsigned pc = 0;
    for (;;) {
        switch (prog[pc++]) {
        case 0: return 0;
        case 1: st[sp++] = prog[pc++]; break;
        case 2: sp--; st[sp-1] += st[sp]; break;
        case 3: sp--; st[sp-1] -= st[sp]; break;
        case 4: sp--; st[sp-1] *= st[sp]; break;
        case 5: st[sp] = st[sp-1]; sp++; break;
        case 6: { int v = st[--sp]; unsigned a = prog[pc++]; if (v) pc = a; break; }
        case 7: printf("%d\n", st[--sp]); break;
        default: puts("bad opcode"); return 1;
        }
    }
}
