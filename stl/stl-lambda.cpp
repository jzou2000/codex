#include <algorithm>
#include <list>
#include <vector>
#include <iostream>

using namespace std;

/*
   [](args) { statments; return value; }

   [=](args) { statments; return value; }       // by value

   [&](args) { statments; return value; }       // by reference

*/

int main()
{
    list<int> c = { 1, 2, 3, 4, 5, 6, 7, 8, 9 };

    transform(c.cbegin(), c.cend(),
             c.begin(),
             [](int v) { return v*v*v; });

    for (auto e: c) {
        cout <<  e << ' ';
    }
    cout << endl;

    return 0;
}

// output
// ./stl-lambda
// 1 8 27 64 125 216 343 512 729


