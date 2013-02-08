#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef TRUE
#define TRUE    -1
#define FALSE   0
#endif

int foo(int);
int bar(int);
char* stick(int);
void foo_action(int);

#define BUFSIZE         256
int
main(int argc, char* argv[])
{
    char buf[BUFSIZE];
    char cmd[BUFSIZE];
    int repeat;

    while (TRUE) {
        printf("cmd repeat: ");
        if (!fgets(buf, sizeof(buf), stdin))
            break;
        sscanf(buf, "%s %d", &cmd, &repeat);
        if (!strcmp(cmd, "foo")) {
            //printf("foo(%d)\n", repeat);
            foo(repeat);
        }
        else if (!strcmp(cmd, "bar")) {
            //printf("bar(%d)\n", repeat);
            bar(repeat);
        }
        else {
            printf("unknown\n");
        }
    }
    printf("\n");

    return 0;
}


int
foo(int repeat)
{
    int n;

    for (n = 0; n < repeat; n++) {
        printf("foo: %d\n", n);
        foo_action(n);
    }
    return 0;
}

void
foo_action(int count)
{
    int n;
    for (n = 0; n < count; n++) {
        unsigned size = 1000*1000*10;
        char* p = (char*) calloc(size, sizeof(char));
        if (p) {
            int i;
            for (i = 0; i < size; i++)
                p[i] = (char)(i&0xff);
        }
        free(p);
        p = stick(n > 78 ? 78 : n);
        if (p) {
            printf("%s\n", p);
            free(p);
        } else {
            printf("%s\n", "");
        }
    }
}

char*
stick(int count)
{
    char* s = NULL;
    if (count > 0)
        s = (char*) malloc(count + 1);
    if (s) {
        memset(s, '*', count);
        s[count] = 0;
    }
    return s;
}


int
bar(int repeat)
{
    int n;

    for (n = 0; n < repeat; n++) {
        printf("------------------bar: %d\n", n);
        sleep(1);
    }
    return 0;
}

