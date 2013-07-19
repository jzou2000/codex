#include <future>
#include <chrono>
#include <random>
#include <iostream>
#include <exception>

using namespace std;

int doSomething(char c)
{
    std::default_random_engine dre(c);
    std::uniform_int_distribution<int> id(10, 1000);

    for (auto i = 0; i < 10; ++i) {
        this_thread::sleep_for(chrono::milliseconds(id(dre)));
        cout.put(c).flush();
    }
    return c;
}

int foo()
{
    return doSomething('F');
}

int bar()
{
    return doSomething('b');
}

int main()
{
    cout << "Starting bar() in background"
         << " and foo() in foreground" << endl;

    std::future<int> result1(std::async(launch::async, bar));
    int result2 = foo();

    try {
        int result = result1.get() + result2;
        cout << endl << "result of foo+bar: " << result << endl;
    }
    catch (exception& e) {
        cout << endl << "exception: " << e.what() << endl;
    }
    catch (...) {
        cout << endl << "exception caugth" << endl;
    }

    return 0;
}


