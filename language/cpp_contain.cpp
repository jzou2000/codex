#include <iostream>
#include <vector>

using namespace std;

class X {
    private:
    static int seed;

    private:
        int id;
    public:
        X() {
            id = seed++;
            cout << "X " << id << " is created" << endl;
        }
        X(const X& ref) {
            id = seed++;
            cout << "X " << id << " is created from " << ref.id << endl;
        }
        ~X() {
            cout << "X " << id << " is destroyed" << endl;
        }
        friend ostream& operator<<(ostream& os, X& x) {
            os << "X(" << x.id << ")";
            return os;
        }
};

int X::seed = 0;


class A {
    private:
        vector<X> list;
        string name;
    public:
        A(const char* name) {
            this->name = name;
            cout << "A::" << this->name << " is created" << endl;
        }
        ~A() {
            cout << "A::" << this->name << " is destroyed" << endl;
        }
        void add(X x) {
            cout << "x " << x << " is added\n";
            list.push_back(x);
        }
};

int main()
{
    X x;
    A *a = new A("batch");

    a->add(x);
    delete a;
    cout << "a is deleted" << endl;
    return 0;
}

