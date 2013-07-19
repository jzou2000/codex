#include <algorithm>
#include <list>
#include <vector>
#include <iostream>

using namespace std;

/*
 template <typename InputIterator, typename OutputIterator>
   OutputIterator copy(InputIterator first, InputIterator last,
                     OutputIterator result);
*/

int main()
{
    list<int> c1 = { 1, 2, 3, 4, 5, 6, 7, 8, 9 };
    //vector<int> c2;
    vector<int> c2(15);

    // copy() algorithm overwrites the destination, which means
    // c2 must have enough elements from c2.begin, that defines by
    // c1.cbegin and c1.cend, otherwise the result is undefined.
    //
    // An alternative solution is to use insert iterator for result.
    //  back_inserter(container)        by using push_back(val)
    //  front_inserter(container)       by using push_front(val)
    //  inserter(container, pos)        by using insert(pos, val)
    copy(c1.cbegin(), c1.cend(), c2.begin());

    for (auto e: c2) {
        cout <<  e << ' ';
    }
    cout << endl;

    return 0;
}

// output with vector<int> c2;          // line 11
// ./stl-copy
// Segmentation fault
//
// output with vector<int> c2(20);      // line 12
// ./stl-copy
// 1 2 3 4 5 6 7 8 9 0 0 0 0 0 0


