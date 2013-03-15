/*
 * Implement quick sort algorithm in C, used to compare with 
 * different implementations and languages.
 *
 * Shuffled sequence data are generated by shuffle.py.
 *
 * The result on a linux (fedora 18) with 4 cores @2.40G 4GB Mem
 *
 * [jzou@luigi language]$ ./cqsort r1m.txt       # 1000000 shuffled data
 * load: 0.17
 * duplicate: 0.00
 * qsort: 0.27
 * validate: 0.00
 * buildin: 0.26
 * 
 *
 * for -O3 optimization
 *
 * load: 0.16
 * duplicate: 0.00
 * qsort: 0.12
 * validate: 0.00
 * tqsort: 0.12
 * buildin: 0.18
 * 
 */


#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <sys/time.h>

#define swap(a, b) { t=a;a=b;b=t; }

float timeit(void)
{
    static struct timeval tv_last = {0, 0};
    struct timeval tv = {0, 0};

    float elapse = 0.0;

    if (0 == gettimeofday(&tv, NULL)) {
        elapse = (tv.tv_sec - tv_last.tv_sec)
                + (tv.tv_usec - tv_last.tv_usec) /1000000.0;
    }
    tv_last = tv;
    return elapse;
}

void dumpi(int* v, int size)
{
    int i, n = 0;
    for (i = 0; i < size; i++) {
        n += printf("%d ", v[i]);
        if (n >= 74) {
            printf("\n");
            n = 0;
        }
    }
    if (n)
        printf("\n");
}

int validate(int* v, int size)
{
    int i;
    for (i = 0; i < size; i++)
        if (i != v[i]) return 0;
    return 1;
}


void cqsort(int* v, int start, int end)
{
    if (start >= end)
        return;

    int m = (start + end)/2;
    int pivot = v[m];
    int t, i;
    if (m < end)
        swap(v[m], v[end]);

    m = start;
    for (i = start; i < end; i++) {
        if (v[i] < pivot) {
            swap(v[i], v[m]);
            m += 1;
        }
    }
    swap(v[m], v[end]);
    cqsort(v, start, m - 1);
    cqsort(v, m + 1, end);
}


int intcmp(const void* a, const void* b)
{
    return *((int*)a) - *((int*)b);
}

#define PAGE_SIZE       64*1024

int main(int argc, char* argv[])
{
    int size = 0, count = 0;
    int i;
    int *v = NULL;
    FILE* fp = fopen(argv[1], "r");

    timeit();
    if (fp) {
        while (fscanf(fp, "%d", &i) != EOF) {
            if (size < count + 1) {
                v = (int*) realloc(v, sizeof(int) * (size + PAGE_SIZE));
                if (!v) {
                    printf("Bad alloc\n");
                    break;
                }
                size += PAGE_SIZE;
            }
            v[count++] = i;
        }
        fclose(fp);
    } else {
        printf("Fail to load %s\n", argv[1]);
        return 1;
    }
    printf("load: %.2f\n", timeit());

    timeit();
    int *v2 = (int*) calloc(sizeof(int), count);
    for (i = 0; i < count; i++) {
        v2[i] = v[i];
    }
    printf("duplicate: %.2f\n", timeit());

    timeit();
    cqsort(v, 0, count - 1);
    printf("qsort: %.2f\n", timeit());

    /* validate the result is correct. The input is shuffled
     * from python range(number) */
    i = 0;
    timeit();
    for (i = 0; i < count; i++) {
        if (i != v[i]) {
            printf("validation failed\n");
            break;
        }
    }
    printf("validate: %.2f\n", timeit());

    timeit();
    qsort(v2, count, sizeof(int), intcmp);
    printf("buildin: %.2f\n", timeit());

    return 0;
}

