#! /usr/bin/env perl

use strict;
use Time::HiRes qw (time);
use vars qw ( $click );
use subs qw ( qsort click );

=pod
Use quick sort algorithm for data from shuffle.py

The result on a linux (fedora 18) with 4 cores @2.40G 4GB Mem

[jzou@luigi language]$ ./qsort.pl r1m.txt
load: 0.46
duplicate: 0.17
qsort: 12.87
validate: 0.12
buildin: 1.18

=cut

sub qsort
{
    my ($data, $start, $end) = @_;
    
    return if ($start >= $end);
    my $m = int(($start + $end)/2);
    my $pivot = $data->[$m];
    my $t;
    if ($m < $end) {
        $t = $data->[$m];
        $data->[$m] = $data->[$end];
        $data->[$end] = $t;
    }
    $m = $start;
    for my $i ($start .. $end-1) {
        next if $data->[$i] >= $pivot;
        $t = $data->[$m];
        $data->[$m] = $data->[$i];
        $data->[$i] = $t;
        $m++;
    }
    $t = $data->[$m];
    $data->[$m] = $data->[$end];
    $data->[$end] = $t;
    qsort($data, $start, $m - 1);
    qsort($data, $m + 1, $end);
}

sub click
{
    my $now = $click;
    $click = time();
    $click - $now;
}


eval {
    my @v = ();
    click();
    open F, "$ARGV[0]";
    while (<F>) {
        push @v, $_ foreach split(/\s+/);
    }
    close F;
    printf "load: %.2f\n", click();

    click();
    my @v2 = @v;
    printf "duplicate: %.2f\n", click();

    click();
    qsort(\@v, 0, @v - 1);
    printf "qsort: %.2f\n", click();

    click();
    my $i = 0;
    foreach (@v) {
        if ($i != $_) {
            print "validate failed\n";
            last;
        }
        $i++;
    }
    printf "validate: %.2f\n", click();

    click();
    @v2 = sort { $a <=> $b } @v2;
    printf "buildin: %.2f\n", click();
};
warn $@ if $@;
