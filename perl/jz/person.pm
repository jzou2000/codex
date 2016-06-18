package jz::person;

use Data::Dumper;
use overload (
    q("") => "as_string",
);

sub new {
    my $class = shift;
    my $name = shift;

    my @name = split('\s+', $name);
    my $self = {
	firstName => ucfirst $name[0],
	lastName => ucfirst $name[1],
    };
    bless $self, $class;
    printf "jz::person is created: %s\n", $self->fullName();
    return $self;
}

sub DESTROY {
    my $self = shift;
    printf "jz::person (%s) is deleted\n", $self->fullName();
}

sub fullName {
    my $self = shift;
    my @name = ($self->{firstName}, $self->{lastName});
    join(' ', @name);
}

sub as_string {
    my $self = shift;
    ref($self) . ': ' . $self->fullName();
}

1;

