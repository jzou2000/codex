/***************************************************************************
  This program demonstrates producer/comsumer pattern of multiple-threading.

  Two producer threads feed data to a queue, three consumer threads
  get data from the queue. A mutex and condition variable are used to
  synchronize feeding and getting on the queue.

  The mutex is used for exclusive access of shared data (the queue).
  The condition variable is used to wake up blocked thread(s). In this
  demonstration, consumers are blocked when the queue is empty. When data
  is fed into the queue (by a producer), an arbitery consumer is waken
  up. For simplicity, in this example, the queue increases on demand.
  If the size of the queue is limited, when the queue is full, producers
  should be blocke until more space is available when a consumer fetches
  data.

Note:
    1. copy constructor and destructor of Producer and Consumer are not
       necessary in the demonstrator.
    2. notify_one() is used when data is fed because any one consumer
       is needed to be waken up. notify_all() is used to wake up all
       consumers when the procedure finishes.

***************************************************************************/
#include <future>
#include <mutex>
#include <condition_variable>
#include <chrono>

#include <iostream>
#include <string>
#include <vector>
#include <exception>

#include <queue>

using namespace std;


template <typename T>
class Pipe : public queue<T> {
    public:
	Pipe(int count) : queue<T>(), count(count) {
	}
	virtual ~Pipe(void) {
	}
	bool done(void) { return count == 0; }

    friend class Producer;
    friend class Consumer;

    protected:
	int count;	// count reaches zero, the program exits
	mutex pmutex;
	condition_variable readyVR;
};

class Producer {
    public:
	Producer(string name, Pipe<int>& apipe, int seed = 0, int interval = 1000)
	    : name(name), pipe(apipe), seed(seed), interval(interval) {
	}
	Producer(const Producer& a)
	    : name(a.name), pipe(a.pipe) {
	}
	virtual ~Producer() {
	}

	// Producer is a functor, i.e. entrance of producer thread
	int operator () () {
	    int i = seed;
	    while (true) {
		this_thread::sleep_for(chrono::milliseconds(interval));
		{
		    lock_guard<mutex> lg(pipe.pmutex);
		    if (pipe.done()) {
			pipe.readyVR.notify_all();
			break;
		    }
		    cout << name << " produce " << i << endl;
		    pipe.push(i++);
		    pipe.count--;
		    pipe.readyVR.notify_one();
		}
	    }
	    return seed;
	}

    protected:
	string  name;	    // identify the producer object
	int	seed;	    // base of generated data to distinguish output
	int	interval;   // make producer threads run in different speed
	Pipe<int>& pipe;
};


class Consumer {
    public:
	Consumer(string name, Pipe<int>& apipe)
	    : name(name), pipe(apipe) {
	}
	Consumer(const Consumer& a)
	    : name(a.name), pipe(a.pipe) {
	}
	virtual ~Consumer() {
	}

	// Consumer is a functor, i.e. entrance of consumer thread
	int operator () () {
	    int n = 0;	// count of total data consumed in this thread
	    while (true) {
		//this_thread::sleep_for(chrono::milliseconds(50));
		{
		    // lock_guard is generally used for mutex,
		    // however, with condition variable, unique_lock
		    // should be used because mutex will be locked/unlocked
		    // by the condition variable.
		    unique_lock<mutex> ul(pipe.pmutex);
		    if (pipe.empty()) {
			if (pipe.done()) {
			    break;
			} else {
			    Pipe<int>& p = pipe;
			    // lambda here is optional to demonstrate
			    // advanced wakeup logic
			    pipe.readyVR.wait(ul, [&p, this](){
				    cout << "    " << this->name
				         << " done=" << p.done()
				         << " size=" << p.size() << endl;
					 return p.done() || !p.empty();});
			}
		    } else {
			auto i = pipe.front();
			pipe.pop();
			n++;
			cout << "        " << name
			    << " consume " << i << "  items:" << n << endl;
		    }
		}
	    }
	    return n;
	}

    protected:
	string name;
	Pipe<int>& pipe;
};



int main()
{
    Pipe<int> pipe(22);		// total 22 data are processed

    Producer p1("P1", pipe);
    Producer p2("P2", pipe, 100, 2500);
    Consumer c1("C1", pipe);
    Consumer c2("C2", pipe);
    Consumer c3("C3", pipe);


    try {
	cout << "launch two producers and three consumers" << endl;
	vector<future<int>> r;
	r.push_back(std::async(launch::async, ref(p1)));
	r.push_back(std::async(launch::async, ref(p2)));
	r.push_back(std::async(launch::async, ref(c1)));
	r.push_back(std::async(launch::async, ref(c2)));
	r.push_back(std::async(launch::async, ref(c3)));

	cout << endl << "get final result" << endl;
	int result =0;
	for (future<int> &i : r) {
	    auto n = i.get();
	    cout << "future.get=" << n << endl;
	    result += n;
	}
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


