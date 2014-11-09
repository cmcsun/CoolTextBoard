use strict;

# vipmark for tablecat bbs, by tablecat

sub markup($$$$) {
    my ($str, $dir, $board, $thread) = @_;
    $str =~ s/&gt;&gt;(([1-9][0-9]*[\-\,]?)+)/<a href="$dir\/read.cgi\/$board\/$thread\/$1">&gt;&gt;$1<\/a>/g;
    my $urlpattern = qr{(?:https?|ftp)://[a-z0-9-]+(?:\.[a-z0-9-]+)+(?::[0-9]{4})?(?:[/?](?:[\x21-\x25\x27-\x5A\x5E-\x7E]|&amp;)+)?};
    $str =~ s/($urlpattern)/my $l = markup_escape($1); '<a href="' . $l . '">' . $l . '<\/a>'/eg;
    $str =~ s/^@@(\n[^\n])/\x{3000}$1/gm;
    $str =~ s/(^|\n+)(\x{3000}.+?)(\n\n+|\Z)/$1 . '<p><span lang="ja">' . markup_escape($2) . '<\/span><\/p>' . $3/emgs;
    $str =~ s/(<span lang="ja">)\x{3000}\n/$1/g;
    $str =~ s{(^|\n+)``\n+(.+?)\n+``(\n+|\Z)}
            { my $m = $&; $m =~ /(^|\n+)(\x{3000}.*?)(\n\n+|\Z)/ ? $m : $1 . '<p><code>' . markup_escape($2) . '</code></p>' . $3; }emgs;
    $str =~ s/^&gt;\s?(.*)$/<blockquote>$1<\/blockquote>/mg;
    $str =~ s/(?:<\/blockquote>(\n)<blockquote>|\n+(<blockquote>|<p>)|(<\/blockquote>|<\/p>)\n+)/$1$2$3/g;
    $str =~ s/(\'{6,})/markup_escape($1)/eg;
    $str =~ s/\'{5}(?![\s\'])((?:(?!\n|\'{5}).)+?)(?<![\s\'])\'{5}/<strong><em>$1<\/em><\/strong>/g;
    $str =~ s/(\'{4})/markup_escape($1)/eg;
    $str =~ s/\'{3}(?![\s\'])((?:(?!\n|\'{3}).)+?)(?<![\s\'])\'{3}/<strong>$1<\/strong>/g;
    $str =~ s/\'{2}(?![\s\'])((?:(?!\n|\'{2}).)+?)(?<![\s\'])\'{2}/<em>$1<\/em>/g;
    $str =~ s/\n/<br>/g;
    return (markup_unescape($str), 0);
}

sub markup_escape($) {
    my $str = shift;
    $str =~ s/&gt;/\x{1F}A/g;
    $str =~ s/^``/\x{1F}B/g;
    $str =~ s/'/\x{1F}C/g;
    return $str;
}

sub markup_unescape($) {
    my $str = shift;
    $str =~ s/\x{1F}A/&gt;/g;
    $str =~ s/\x{1F}B/``/g;
    $str =~ s/\x{1F}C/'/g;
    return $str;
}

1;