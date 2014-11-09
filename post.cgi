#!/usr/bin/perl -Tw

use strict;
use CGI::Carp 'fatalsToBrowser';
use Fcntl ':flock';
use File::ReadBackwards;
use lib '.';

BEGIN {
    require "config.pm";
    require "common.pm";
    require "html.pm";
    require "markup.pm";
}

abort('This software is using the default cryptographic secret key')
  if SECRET_KEY eq 'CHANGEME';

# collect data
my %form    = form_data();
my $board   = $form{'board'};
my $thread  = $form{'thread'};
my $subject = $form{'subject'};
my $comment = $form{'message'};
my $name    = $form{'name'};
my $sage    = $form{'sage'};
my $noko    = $form{'noko'};
my $preview = $form{'preview'};
my $spam    = $form{'comment'};
my $ip      = $ENV{'REMOTE_ADDR'}; # HTTP_CF_CONNECTING_IP , REMOTE_ADDR
my $dir     = $ENV{'SCRIPT_NAME'};
my $time    = time;

my $postcount = 1;
my $permasage = 0;
my $closed    = 0;

# sanitize data
($board )  = $board   =~ /^([a-z0-9]+)$/;
($thread)  = $thread  =~ /^([0-9]+)$/;
($subject) = $subject =~ /^([^\n]+)$/;
($name)    = $name    =~ /^([^\n]+)$/;
($sage)    = $sage    =~ /^on$/;
($noko)    = $noko    =~ /^on$/;
($ip)      = $ip      =~ /^([0-9a-fA-F:\.]+)$/;
($dir)     = $dir     =~ /^(.*)\/[^\/]*$/;

# verify data
abort('Spam!') if length $spam > 0;
abort('Tainted!') if (length $subject > 0) && (length $thread > 0) || (length $subject > 0) && $sage || !$ip;
abort('Thread does not exist') if (length $thread > 0) && !-e "$board/res/$thread.html";
if ($ENV{'REQUEST_METHOD'} eq 'POST') {
    abort('Board not defined') if (length $board == 0);
    my %boards = BOARDS;
    my $listed;
    while (my ($key, $value) = each(%boards)) {
        $listed = 1 if $board eq $key;
    }
    abort('Board is not active') unless $listed;
    abort('No subject') if (length $subject == 0) && (length $thread == 0);
    abort('No comment') if length $comment == 0;
}
$name = DEFAULT_NAME unless (length $name > 0);
($name, my $trip) = tripcode($name);
abort('Flood detected')   if -e "$board/res/$time.html" && length $subject > 0;
abort('Post less often')  if ($time - read_log($ip, $time)) <= FLOOD_DELAY;
abort('Subject too long') if length $subject > SUBJECT_LENGTH;
abort('Comment too long') if length $comment > COMMENT_LENGTH;
abort('Name too long')    if length $name    > NAME_LENGTH;
abort('Subject contains a blacklisted item') if blacklist($subject, 'spam.txt');
abort('Comment contains a blacklisted item') if blacklist($comment, 'spam.txt');
abort('Name contains a blacklisted item')    if blacklist($name,    'spam.txt');
abort('Your IP address is blacklisted')      if blacklist($ip,      'ban.txt');

my $newthread = 1 unless $thread;
my ($last_bumped, $last_posted);
if ($thread) {
    ($last_bumped, $last_posted, $closed, $permasage, $postcount, $subject) = read_thread_info($board, $thread);
    $postcount++;
    abort('Post limit reached') if $postcount > POST_LIMIT;
    abort('Thread is closed')   if $closed;
    if (THREAD_NECROMANCY) {
        my $limit = NECROMANCY_DAYS * 86400;
        my $diff;
        if (NECROMANCY_AGE == 0) {
            $diff = $time - $thread;
        }
        elsif (NECROMANCY_AGE == 1) {
            $diff = $time - $last_bumped;
        }
        elsif (NECROMANCY_AGE == 2) {
            $diff = $time - $last_posted;
        }
        if (THREAD_NECROMANCY == 1) {
            $sage = 1 if $diff > $limit;
        }
        elsif (THREAD_NECROMANCY == 2) {
            abort("This thread is too old, you can't reply anymore") if $diff > $limit;
        }
    }
}
else {
    ($thread, $last_bumped, $last_posted) = ($time, $time, $time);
}
$sage = $permasage || $sage ? 1 : 0;

my ($parsed_comment, $malformed) = markup($comment, $dir, $board, $thread);
abort('Comment contains malformed markup') if ($malformed && NO_MALFORMED) && !$preview;

# process data
if ($ENV{'REQUEST_METHOD'} eq 'POST') {
    if (!-d "$board/res/") { mkdir("$board/res", 0755) || die "Cannot create directory: $!"; }
    if ($preview) { print_preview($dir, $board, $name, $trip, $comment, $parsed_comment, $postcount, $sage, $subject, $newthread, $thread) }
    write_thread($dir, $board, $thread, $last_bumped, $last_posted, $closed, $permasage, $postcount, $subject, $name, $trip, $time, $sage, $parsed_comment);
    write_log($ip, $time, $board, $thread, $postcount);
    build_pages($dir, $board);
    redirect($dir, $board, $thread, $postcount, $sage, $noko);
}
else {
    my %boards = BOARDS;
    while (my ($key, $value) = each(%boards)) {
        if (!-d "$key/") { mkdir("$key", 0755) || die "Cannot create directory: $!"; }
        build_pages($dir, $key);
    }
    redirect($dir, 0, 0, 0, 0, 0);
}