#include <algorithm>
#include <list>
#include <vector>
#include <iostream>

using namespace std;

/*

*/

class A {
    public:
        A() { cout << "A.created" << endl; }
        ~A() { cout << "A.deleted" << endl; }
        virtual void foo() { cout << "A.foo" << endl; }
};

class B : public A {
    public:
        B() { cout << "B.created" << endl; }
        ~B() { cout << "B.deleted" << endl; }
        virtual void foo() { cout << "B.foo" << endl; }
};

class C {
    public:
        C() { cout << "C.created" << endl; }
        ~C() { cout << "C.deleted" << endl; }
        virtual void foo() { cout << "C.foo" << endl; }
};

int main()
{
    {
        B b;
        C c;
        A* ap = nullptr;
        B* bp = &b;
        C* cp = &c;

        cout << "bp=" << bp << endl;
        cout << "cp=" << cp << endl;
        {
            ap = (A*) bp;  
            cout << "ap=" << ap << endl;
            cout << "no problem: B cast to A" << endl;
        }
        {
            B* p = dynamic_cast<B*>(ap);  
            cout << "p=" << p << endl;
            cout << "no problem: A cast to B" << endl;
        }
        {
            B* p = dynamic_cast<B*>(cp);  
            cout << "p=" << p << endl;
            cout << "no problem: C cast to B" << endl;
        }
        cout << "end of scope" << endl;
    }

    cout << "The End" << endl;
    return 0;
}

// output
// ./stl-lambda
// 1 8 27 64 125 216 343 512 729


