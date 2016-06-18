#! /usr/bin/env perl

use XML::XPath;

foreach (@INC) {
    print "    $_\n";
}

sub dumpNode {
    my $n = shift;

    my $s = sprintf "%s\n", $n->getName();
    my @a = ();
    for my $a ($n->getAttributes()) {
	push @a, (sprintf "%s=%s", $a->getName(), $a->getData());
    }
    $s .= sprintf("[%s]\n", join(' ', @a)) if (@a>0);
    my $t = $n->string_value();
    $s .= "$t\n" if (defined $t and length($t));
    $s;
}

my $fname = shift @ARGV;
my $xp = XML::XPath->new(filename => $fname);
my $context = undef;
while (1) {
    printf "input xpath: ";
    my $p = <STDIN>;
    last unless defined($p);
    chomp $p;
    eval {
	my @n = $xp->findnodes($p, $context);
	printf "----\n%s\n", dumpNode($_) for (@n);
	$context = $n[0] if (@n > 0);
    };
    if ($@) {
	print "ERROR: $@\n";
    }
}
print "\n";

