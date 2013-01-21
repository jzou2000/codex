#include <execinfo.h>
#include <stdio.h>
#include <stdlib.h>

const char* bar(const char* ps);
int foo(int pi, const char* ps);
void backtrace_demo(void);

int
foo(int pi, const char* ps)
{
    printf("foo: %d %s\n", pi, ps);
    bar(ps);
    return pi;
}

const char*
bar(const char* ps)
{
    printf("bar: %s\n", ps);
    backtrace_demo();
    return ps;
}

void
backtrace_demo(void)
{
#define MAX_BTS         128
    void* btbuf[MAX_BTS];
    int nbt;
    char ** s;

    nbt = backtrace(btbuf, MAX_BTS);
    s = backtrace_symbols(btbuf, nbt);
    if (s) {
        int n;
        for (n = 0; n < nbt; n++) {
            printf("%2d: %s\n", n, s[n]);
        }
        free(s);
    }
}

int
main()
{
    foo(100, "hello");

    return 0;
}



