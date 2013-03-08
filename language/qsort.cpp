/*
 * Implement quick sort algorithm in C++, used to compare with 
 * different implementations and languages.
 *
 * Shuffled sequence data are generated by shuffle.py.
 *
 * The result on a linux (fedora 18) with 4 cores @2.40G 4GB Mem
 *
 * [jzou@luigi language]$ ./qsort r1m.txt
 * size=1000000
 * load: 0.19
 * qsort: 0.50
 * validate: 0.03
 * std::sort: 0.50
 * 
 */

#include <exception>
#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm>

#include <sys/time.h>


using namespace std;

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


typedef vector<int> V;

void dumpq(V& v)
{
    for (V::iterator it = v.begin(); it != v.end(); ++it) {
        cout << *it << ' ';
    }
    cout << endl;
}

void _qsort(V& v, int start, int end)
{
    if (start >= end)
        return;

    int m = (start + end)/2;
    int pivot = v[m];
    int t;
    if (m < end)
        swap(v[m], v[end]);

    m = start;
    for (int i = start; i < end; i++) {
        if (v[i] < pivot) {
            swap(v[i], v[m]);
            m += 1;
        }
    }
    swap(v[m], v[end]);
    _qsort(v, start, m - 1);
    _qsort(v, m + 1, end);
}

void qsort(V& v)
{
    _qsort(v, 0, v.size() - 1);
}


int main(int argc, char* argv[])
{
    try {
        std::fstream f(argv[1]);
        if (!f.good())
            throw std::string("Fail to open the file");

        V v;
        int i;
        timeit();
        while ((f >> i)) {
            v.push_back(i);
        }
        float t1 = timeit();
        cout << "size=" << v.size() << endl;

        V v2 = v;

        timeit();
        qsort(v);
        float t2 = timeit();

        /* validate the result is correct. The input is shuffled
         * from python range(number) */
        i = 0;
        timeit();
        for (V::iterator it = v.begin(); it != v.end(); ++it, ++i) {
            if (i != *it) {
                cerr << "qsort failed" << endl;
                break;
            }
        }
        float t3 = timeit();

        timeit();
        sort(v2.begin(), v2.end());
        float t4 = timeit();

        cout.setf(std::ios::fixed);
        cout.precision(2);
        cout << "load: " << t1 << endl;
        cout << "qsort: " << t2 << endl;
        cout << "validate: " << t3 << endl;
        cout << "std::sort: " << t4 << endl;

    }
    catch (std::string& e) {
        cerr << e << endl;
    }
    catch (exception& e) {
        cerr << "exception: " << e.what() << endl;
    }
    return 0;
}

