This is a small project to demonstrate the performance difference between
different languages, including:

    c	    The common-acknowledged fastest language (except assembly),
            it is used as the base of comparison.

    c++	    As descendant of c, it is the most common used language
            for large-scale, performance critical systems and applications.
	    It would be interesting to show what is the performance cost
	    for its features like OOP, generic, STL.

    java    Modern common used language. Is it still 20-times slower as
            it was first invented? How good is JIT and years-of-
	    optimization?

    perl    Traditional system level script language, declared the fastest
            script language. However perl suffers from the reputation
	    of "write-then-never-read"

    python  Modern system level script language, especially promoted by
            google. With all benifits for programmers, how about speed?

Because multi-threading is such a hot topic, two modules are added to c++
language to show how good we can achieve by multi-threading, deducting the
cost of threading (synchronization, context switching, etc)

    NOTE: multithreading versions are also exercises of more C++ features
    including OOP, STL, C++11

The comparison emphasizes the languages themselves, so an easy-implemented
cpu-intensive process, quick-sort, is chosen. Libraries (e.g. IO, build-in
sort are usually implemented by C, they are meassured just for references)

             qsort     load      build-in comment
    -----------------------------------------------------------------------
    C        0.50      0.58      0.84
    C++      0.506     0.506     0.419    little cost, great libs/STL
    C++-m    0.398     0.497     0.448    mt works a little, too much cost
    C++-m2   0.246     0.498     0.412    mt works great
    java     0.64      3.19      2.118    good job, java (v1.8)
    perl     43.73     1.65      4.87     io fast enough, slow cmp c
    python   30.4      2.83      4.06     python exceed perl

note:
* platform: virtualbox/debian7(64b) runs on iMac 2011, i5@2.5G x3, 4GB mem
* test data is generated by shuffle.py, which shuffles range(5000000)
    ./shuffly.py 5000000 r5m.txt
* build and launch
    make
    o/cqsort r5m.txt
    o/qsort r5m.txt
    o/qsort-m r5m.txt
    o/qsort-m2 r5m.txt
    java qsort r5m.txt
    ./qsort.pl r5m.txt
    ./qsort.py r5m.txt
* to make neutral language-specific comparison, all programs (except multi-
  versions) are implemented as close as possible, e.g. qsort.cpp is not
  designed as OOP. However, qsort-m.cpp and qsort-m2.cpp look more like
  C++ programs.

