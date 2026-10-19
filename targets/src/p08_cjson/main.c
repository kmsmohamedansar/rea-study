#include <stdio.h>
#include <stdlib.h>
#include "cJSON.h"
/* reads up to 4095 bytes of JSON on stdin and prints the string value of the top-level "name"
   field. Bad JSON: prints "parse error", exit 1. No such string field: prints "missing", exit 0. */
int main(void) {
    char buf[4096];
    size_t n = fread(buf, 1, sizeof buf - 1, stdin);
    buf[n] = 0;
    cJSON *j = cJSON_Parse(buf);
    if (!j) { puts("parse error"); return 1; }
    cJSON *f = cJSON_GetObjectItemCaseSensitive(j, "name");
    if (cJSON_IsString(f) && f->valuestring) printf("%s\n", f->valuestring);
    else puts("missing");
    cJSON_Delete(j);
    return 0;
}
