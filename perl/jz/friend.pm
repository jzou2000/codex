package jz::friend;

use jz::person;

use Data::Dumper;

our @ISA = qw ( jz::person );

sub new {
    my $class = shift;
    my $name = shift;

    my $self = $class->SUPER::new($name);
    bless($self, $class);
    printf "jz::friend is created: %s\n", $self->fullName();
    return $self;
}

sub DESTROY {
    my $self = shift;
    printf "jz::friend (%s) is deleted\n", $self->fullName();
}

sub greet {
    my $self = shift;
    printf "Hi, my name is %s\n", $self->fullName();
}

=pod
sub fullName {
    my $self = shift;
    my @name = ($self->{lastName}, $self->{firstName});
    join(', ', @name);
}
=cut
1;

