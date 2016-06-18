#! /usr/bin/env perl

use strict;
use warnings;

use Data::Dumper;
use jz::friend;
#use jz::person;

sub foo {
    printf "enter foo\n";
    my $f = jz::friend->new('jason          zou');
    $f->greet();
    print "foo=$f\n";
}

printf "begin\n";
eval {
    foo();
};
print "ERROR: $@\n" if ($@);
printf "end\n";
