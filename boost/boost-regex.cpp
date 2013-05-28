#include <iostream>
#include <fstream>
#include <vector>
#include <boost/regex.hpp>

using namespace std;

typedef vector<string>  vs;

vector<string>& load(const char* fname)
{
    vector<string> *v = new vector<string>();

    try {
        cout << "load from file: " << fname << endl;
        ifstream f(fname);
        char buf[BUFSIZ];
        cout << "BUFSIZ=" << sizeof(buf) << endl;
        int i = 0;
        while (f.good()) {
            f.getline(buf, sizeof(buf));
            cout << ++i << " [" << buf << "]" << endl;;
            v->push_back(string(buf));
        }
    }
    catch (exception& e) {
        cerr << "exception: " << e.what() << endl;
    }

    cout << endl << "================ finish loading" << endl << endl;
    return *v;
}

template <typename T>
void dump(vector<T>& v)
{
    cout << "dump: size=" << v.size() << endl;
    vector<string>::iterator i = v.begin();
    int n = 0;
    while (i != v.end()) {
        cout << ++n << ": " << *i << endl;
        ++i;
    }
    cout << "=========end-of-dumping" << endl;
}

void reg_find_all(vector<string>& v, boost::regex& re)
{
    vector<string>::iterator i = v.begin();
    vector<string>::iterator ie = v.end();
    int n = 1;
    boost::smatch m;

    cout << "========== reg_find_all: " << re << endl;
    for (; i != ie; ++i, ++n) {
        if (boost::regex_search(*i, m, re)) {
            cout << n << ": " << endl;
            //cout << "    m.size=" << m.size() << endl;
            //cout << "    m.prefix=" << m.prefix() << endl;
            //cout << "    m.suffix=" << m.suffix() << endl;
            cout << "    m[0]: " << m[0] << endl;
            //cout << "m[0]: first=" << m[0].first
            //     << "  " << m[0]
            //     << "  second=" << m[0].second << endl;
            if (m.size() > 1) {
                for (int j = 1; j < m.size(); ++j) {
                    cout << "        m[" << j << "]: " << m[j] << endl;
                    //cout << "        m[" << j << "]: first=" << m[j].first
                    //    << "  " << m[j]
                    //    << "  second=" << m[j].second << endl;
                }
            }
        }
    }

}

int main(int argc, char* argv[])
{
    vs& v = load((const char*) argv[1]);
    dump(v);

    boost::regex eWord("\\b[A-Z]\\w*\\b");
    boost::regex etag("<.+?>");
    boost::regex etagvalue("<(.+?)>(.+?)</\\1>", boost::regex::perl);

    reg_find_all(v, eWord);
    reg_find_all(v, etag);
    reg_find_all(v, etagvalue);

    return 0;
}

