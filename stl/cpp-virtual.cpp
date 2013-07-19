// 
// Demonstrate virtual functions, especially virtual destructor
// in polymorphism.
//
#include <iostream>

using namespace std;

class A {
    public:
        A(string a) : name(a) { cout << "A::A " << name << endl; }
        virtual ~A() { cout << "A::~A " << name << endl; }
        virtual void foo() { cout << "A::foo " << name << endl; }
    protected:
        string name;
};

class B : public A {
    public:
        B(string a) : A(a) { cout << "B::B " << name << endl; }
        ~B() { cout << "B::~B " << name << endl; }
        void foo() { cout << "B::foo " << name << endl; }
};

int main()
{
    A  *p = new A("a");
    p->foo();
    delete p;

    cout << endl << "pointer to an object of derived class" << endl;
    p = new B("b");
    p->foo();
    delete p;   // only A::~A is called if destructor is not virtual

    return 0;
}


