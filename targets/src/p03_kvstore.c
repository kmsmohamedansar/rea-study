#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* Key/value store driven by lines on standard input:
   set KEY VALUE | get KEY | del KEY | count | dump | quit.
   Chained hash table, 16 buckets, hash = djb2 (start 5381, h = h*33 + c) mod 16.
   set prints "ok" (replaces an existing key). get prints the value or "missing".
   del prints "deleted" or "missing". count prints the number of keys. dump prints
   KEY=VALUE lines bucket by bucket. quit and end of input exit 0.
   Any other command prints "error" and exits with code 4. */
typedef struct E { char *k, *v; struct E *n; } E;
static E *tab[16];
static unsigned h(const char *s) { unsigned x = 5381; while (*s) x = x * 33 + (unsigned char)*s++; return x % 16; }
static E *find(const char *k) { for (E *e = tab[h(k)]; e; e = e->n) if (!strcmp(e->k, k)) return e; return 0; }
int main(void) {
    char line[256], cmd[16], a[64], b[64];
    while (fgets(line, sizeof line, stdin)) {
        a[0] = b[0] = 0;
        if (sscanf(line, "%15s %63s %63s", cmd, a, b) < 1) continue;
        if (!strcmp(cmd, "set")) {
            E *e = find(a);
            if (e) { free(e->v); e->v = strdup(b); }
            else { e = malloc(sizeof *e); e->k = strdup(a); e->v = strdup(b); e->n = tab[h(a)]; tab[h(a)] = e; }
            puts("ok");
        } else if (!strcmp(cmd, "get")) {
            E *e = find(a); puts(e ? e->v : "missing");
        } else if (!strcmp(cmd, "del")) {
            E **pp = &tab[h(a)]; int done = 0;
            while (*pp) { if (!strcmp((*pp)->k, a)) { E *d = *pp; *pp = d->n; free(d->k); free(d->v); free(d); done = 1; break; } pp = &(*pp)->n; }
            puts(done ? "deleted" : "missing");
        } else if (!strcmp(cmd, "count")) {
            int n = 0; for (int i = 0; i < 16; i++) for (E *e = tab[i]; e; e = e->n) n++;
            printf("%d\n", n);
        } else if (!strcmp(cmd, "dump")) {
            for (int i = 0; i < 16; i++) for (E *e = tab[i]; e; e = e->n) printf("%s=%s\n", e->k, e->v);
        } else if (!strcmp(cmd, "quit")) {
            return 0;
        } else { puts("error"); return 4; }
    }
    return 0;
}
