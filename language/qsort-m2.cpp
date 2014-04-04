/*
 * Implement quick sort algorithm in C++, with multi-threads.
 *
 * This program is a improved version of qsort-m.cpp, which still has
 * too much threading add-on cost. Because there is no relavent action
 * in different subranges once subranges are split in the algorithm,
 * it is even better to pre-split the whole range into several big sub-
 * ranges. Each thread works completely independently and wait/notify
 * are eliminated completely. In an ideal case, the whole range is splitted
 * into the same number of subranges with the number of threads. However
 * it is very difficult to split equal sub-ranges, so we split the whole
 * range into N*workers subranges, each worker randomly executes N ranges
 * thus each worker has almost equivalent work load.
 *
 * In qsort-m.cpp, the complexity of threading is O(log(N)),
 *  where N is total number of elements to sort, and assume each pivot
 *  splits two equal sub-ranges.
 * In qsort-m2.cpp, the complexity of threading is O(1).
 *
 *
 * ./qsort-m2 r5m.txt       # 5,000,000 shuffled data
 * load: 0.481
 *     5000000 items
 * duplicate: 0.009
 * qsort: 0.265
 * validate: 0.004
 * std::sort: 0.440
 * 
 */

#include <exception>
#include <iostream>
#include <fstream>
#include <iterator>
#include <vector>
#include <queue>
#include <algorithm>
#include <chrono>

#include <future>
#include <mutex>
#include <condition_variable>


using namespace std;
typedef vector<int> V;


namespace codex {
    template <typename T>
    class QuickSort {
	public:
	    QuickSort(T& data) : data_(data) {}
	    virtual void run(unsigned workers = 4);

	protected:
	    typedef typename T::iterator Iterator;

	    // can be replaced with pair<>, used as a demonstration
	    // of nested class
	    class Task {
		public:
		    Task() { }
		    Task(Iterator begin, Iterator end)
			: begin(begin), end(end) {}
		    Task(const Task& t) : begin(t.begin), end(t.end) {}

		    Iterator begin, end;
	    };

	    Iterator pivot(Iterator begin, Iterator end);
	    void sort(Iterator begin, Iterator end);
	    int worker(void);

	protected:
	    T&			data_;
	    queue<Task> 	tasks;
	    mutex		pmutex;

	    const unsigned DefaultSegmentsPerWorker = 50;
	    const unsigned DefaultElementsPerSegment = 10000;
    };



    // a single sort iteration:
    // choose any number as pivot (in this example, we choose the middle
    // item in the subset) and put all items that are smaller than
    // the pivot before the pivot and all items that are larger than
    // the pivot after it.
    // the pivot iterator is returned.

    template <typename T>
    typename QuickSort<T>::Iterator QuickSort<T>::pivot(Iterator begin, Iterator end)
    {
	// choose any number in the subset as pivot, in this example,
	// we choose the item in the middle of the subset
        auto m = begin + (end - begin)/2;
        auto last = --end;
        auto pivot = *m;
        if (last - m > 0)
            swap(*m, *last);
    
        m = begin;
        for (auto i = begin; i != last; ++i) {
            if (*i < pivot) {
                swap(*i, *m);
                ++m;
            }
        }
        swap(*m, *last);
	return m;
    }

    template <typename T>
    void QuickSort<T>::run(unsigned workers)
    {
	if (data_.size() <= 1)		// nothing to do
	    return;

	if (workers <= 1) {		// let one thread do everything
	    sort(data_.begin(), data_.end());
	    return;
	}

	// figure out how many segments the whole work can be split

	unsigned total_elements = data_.end() - data_.begin();
	unsigned segments = DefaultSegmentsPerWorker * workers;
	while (total_elements / segments < DefaultElementsPerSegment) {
	    segments /= 2;
	    if (segments <= 1) {
		segments = 1;
		break;
	    }
	}
	if (workers > segments)
	    workers = segments;
	if (workers <= 1) {		// let one thread do everything
	    sort(data_.begin(), data_.end());
	    return;
	}

	// split the whole work into segments/subworks (hopefully)

	tasks.push(Task(data_.begin(), data_.end()));
	while (tasks.size() < segments) {
	    auto t = tasks.front();
	    tasks.pop();

	    typename QuickSort<T>::Iterator m = pivot(t.begin, t.end);

	    bool newseg = false;
	    if (m - t.begin > 1) {
		tasks.push(Task(t.begin, m));
		newseg = true;
	    }

	    if (t.end - m > 1) {
		tasks.push(Task(m + 1, t.end));
		newseg = true;
	    }
	    if (!newseg) break;
	}
	segments = tasks.size();
	if (segments < workers) workers = segments;

	// launch workers and try to process simultaneously

	vector<future<int>> result;
	for (int i = 0; i < workers - 1; ++i) {
	    result.push_back(std::async(launch::async,
			&QuickSort<T>::worker, this));
	}
	worker();	// this thread is also a worker
	int r = 0;
	for (future<int> &i : result) {
	    r += i.get();
	}
    }

    // entrance of worker thread

    template <typename T>
    int QuickSort<T>::worker(void)
    {
	while (true) {
	    QuickSort<T>::Task t;
	    // get next available task/segment from the shared task queue
	    {
		lock_guard<mutex> lg(pmutex);
		if (tasks.empty())
		    break;			// finish!
		t = tasks.front();
		tasks.pop();
	    }
	    // then sort it
	    sort(t.begin, t.end);
	}
	return 0;
    }

    // single-task version

    template <typename T>
    void QuickSort<T>::sort(Iterator begin, Iterator end)
    {
	typename QuickSort<T>::Iterator m = pivot(begin, end);
	if (m - begin > 1)
	    sort(begin, m);
	if (end - m > 1)
	    sort(m + 1, end);
    }




}	// end of namespace


// Return time elapsed since last call, in seconds (accurate to millisec).

float timeit(void)
{
    using namespace std::chrono;
    static system_clock::time_point tp_last;

    system_clock::time_point now = system_clock::now();
    milliseconds ms = duration_cast<milliseconds>(now - tp_last);
    tp_last = now;

    return ms.count()/1000.0;
}

#ifdef DEBUG
template<typename V>
void dumpq(V& v)
{
    for (auto it = v.begin(); it != v.end(); ++it) {
        cout << *it << ' ';
    }
    cout << endl;
}
#endif


int main(int argc, char* argv[])
{
    try {
	if (argc == 1 || string(argv[1]) == string("-h")) {
	    cout << "usage: " << argv[0]
		 << " data-file [ number-of-threads=4 ]" << endl;
	    return 0;
	}

        cout.setf(std::ios::fixed);
        cout.precision(3);

        std::fstream f(argv[1]);
        if (!f.good())
            throw std::string("Fail to open the file");
	unsigned workers = argc > 2 ? stoi(argv[2]) : 4;

        V v;
	timeit();
	copy(istream_iterator<int>(f),
		istream_iterator<int>(),
		back_inserter(v));
        cout << "load: " << timeit() << endl;
        int size = v.size();
	cout << "    " << size << " items" << endl;

        timeit();
        V v2 = v;
        cout << "duplicate: " << timeit() << endl;

	codex::QuickSort<V> qs(v);
        timeit();
	qs.run(workers);
        cout << "qsort: " << timeit() << endl;

        // validate the result is correct.
	// The input is shuffled from python range(number)
        int i = 0;
        timeit();
        for (auto it = v.begin(); it != v.end(); ++it, ++i) {
            if (i != *it) {
                cerr << "qsort failed" << endl;
                break;
            }
        }
        cout << "validate: " << timeit() << endl;

        timeit();
        sort(v2.begin(), v2.end());
        cout << "std::sort: " << timeit() << endl;
    }
    catch (std::string& e) {
        cerr << e << endl;
    }
    catch (exception& e) {
        cerr << "exception: " << e.what() << endl;
    }
    return 0;
}

