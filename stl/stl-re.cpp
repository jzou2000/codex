#include <regex>
#include <iostream>

using namespace std;


int main()
{
    //regex reg1("<(.*?)>.*</\\1>");
    string s =  string("<(.*)>.*</\\1>");
    cout << "pattern=" << s << endl;;

    regex reg1(s);
    //count << "reg1=" << reg1 << endl;
    bool found;

    found = regex_match("<tag>value</tag>", reg1);
    cout << found << endl;

    return 0;
}

