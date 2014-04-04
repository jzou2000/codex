/***************************************************************************
  This is a simple demonstration of multiple-threading with future/async.
  The difference with stl-async.cpp is that a function object is used
  to launch a thread.

  The function object can be passed by value or by reference. See the
  output of the program. It seems that by reference is appreciated in
  most cases.

  Program output:
-------- AsyncApp.first(1) is created
-------- AsyncApp.second(2) is created
launch two threads
-------- AsyncApp.first(3<=1) is created
-------- AsyncApp.first(4<=3) is created
-------- AsyncApp.first(3<=1) is deleted
AsyncApp.second(2) is called: 
AsyncApp.first(4<=3) is called: 
CEget final result
CEECEECCCCEECCECEE-------- AsyncApp.first(4<=3) is deleted

result: 6
-------- AsyncApp.second(2) is deleted
-------- AsyncApp.first(1) is deleted

***************************************************************************/
#include <future>
#include <chrono>
#include <random>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <exception>

using namespace std;

class AsyncApp {
    public:
	// constructor, copy constructor and destructor
	// are used to trace object life.

	AsyncApp(string name) : name(name) {
	    id = seed++;
	    ostringstream os;
	    os << "AsyncApp." << name << "(" << id << ")";
	    name_id = os.str();
	    cout << "-------- " << name_id << " is created" << endl;
	}
	AsyncApp(const AsyncApp& a) {
	    id = seed++;
	    name = a.name;
	    ostringstream os;
	    os << "AsyncApp." << a.name << "(" << id << "<=" << a.id << ")";
	    name_id = os.str();
	    cout << "-------- " << name_id << " is created" << endl;
	}
	virtual ~AsyncApp() {
	    cout << "-------- " << name_id << " is deleted" << endl;
	}

	// overload operator () to make function object
	// this is the actual thread entrance

	int operator () () {
	    cout << name_id << " is called: " << endl;
	    std::default_random_engine dre(id);
	    std::uniform_int_distribution<int> d(10, 1000);

	    for (auto i = 0; i < 10; ++i) {
		this_thread::sleep_for(chrono::milliseconds(d(dre)));
		cout.put('A' + id).flush();
	    }
	    return id;
	}

    protected:
	static int seed;
	int id;
	string name;
	string name_id;
};

int AsyncApp::seed = 1;


int main()
{
    AsyncApp a1("first");
    AsyncApp a2("second");


    try {
	cout << "launch two threads" << endl;

	// launch by value, so the object is copied twice (by async)
	// i.e. two temp objects are created/deleted

	std::future<int> result1(std::async(launch::async, a1));

	// launch by ref, no temp object is created/deleted

	std::future<int> result2(std::async(launch::async, ref(a2)));

	this_thread::sleep_for(chrono::milliseconds(100));
	cout << "get final result" << endl;
        int result = result1.get() + result2.get();
        cout << endl << "result: " << result << endl;
    }
    catch (exception& e) {
        cout << endl << "exception: " << e.what() << endl;
    }
    catch (...) {
        cout << endl << "exception caugth" << endl;
    }

    return 0;
}


