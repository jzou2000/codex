#! /usr/bin/env perl

foreach (0..5) {
    printf "Hello, this is child %d\n", $_;
    sleep(1);
}
exit( 1);
