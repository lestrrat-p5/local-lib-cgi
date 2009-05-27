#!/usr/bin/perl

# XXX note: 
#   must be single file CGI script
#   must not depend on anything other than local::lib and core modules

use strict;
use warnings;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CPAN;

my $CONFIG;
BEGIN {
    my $config = 'local-lib-config.cgi';
    if (-f $config) {
        $CONFIG = require $config;
    }
}

BEGIN {
    my @args;
    if ($CONFIG->{libpath}) {
        unshift @args, $CONFIG->{libpath};
    }
    require local::lib;

    local::lib->import(@args);
}


sub main {
    local $| = 1;
    my $q = CGI->new;

    my $mode = $q->param('mode') || '';
    if ($mode eq 'install') {
        install_mod($q);
    } else {
        control($q);
    }
}

sub install_mod {
    my $q = shift;
    print $q->header('text/plain');
    CPAN::Shell->install($q->param('module'));
}

sub control {
    my $q = shift;

    print
        $q->header(),
        $q->start_html(),
    ;

    print
        $q->start_form(-action => $ENV{SCRIPT_NAME}, -method => 'GET');

    print $q->textfield(
        -name => 'module',
        -size => 30,
        -value => $q->param('module')
    );

    if ($q->param('module')) {
        my $mod;
        {
            local *STDOUT;
            close(STDOUT);
            $mod = CPAN::Shell->expandany($q->param('module'));
        }

        if (! $mod || ! $mod->inst_version) {
            print $q->div($q->param('module') . ": Not installed");        } else {
            print $q->div(
                ($q->param('module')) . ": Installed version is " . $mod->inst_version);
        }
    }

    print
        $q->submit(-name => 'mode', -value => 'check'),
        $q->submit(-name => 'mode', -value => 'install'),
    ;

    print
        $q->end_form(),
        $q->end_html();
}

main();