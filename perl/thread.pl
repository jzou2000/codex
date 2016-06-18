use threads;

my $p1 = threads->create(\&foo, 'a', 1, 10, 10);
my $p2 = threads->create(\&foo, 'b', 2, 10, 20);
my $p3 = threads->create(\&foo, 'c', 1, 5, 30);
print("main\n");

sleep(5);

print "----------join\n";
$p1->join();
$p2->join();
$p3->join();

print "==========end\n";

sub foo {
    my ($nm, $n, $nn, @arg) = @_;

    for my $i (0..$nn) {
	print ' ' x $arg[0], "$nm  $i\n";
	sleep($n);
    }
}


