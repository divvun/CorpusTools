#!/usr/bin/perl -w

use utf8;
use strict;

use IO::File;
use File::Basename;
use Getopt::Long;
use XML::Twig;
use File::Find;
use Carp qw(cluck croak);
use File::Copy;
use Encode;

my $dir = "";
my $lang1 = "";
my $lang2 = "";
my $anchor_file = "";

# Assumption: in $dir there are two subdirs, 
# one for each language and labeled with the language code.

GetOptions (
	"dir=s" => \$dir,
	"lang1=s" => \$lang1,
	"lang2=s" => \$lang2,
	"anchor=s" => \$anchor_file,
);

if(!$anchor_file || ! -e $anchor_file) {
	die "ERROR: Can't open anchor file \"", Encode::decode_utf8($anchor_file), "\"\n";
}

if (-d $dir) {
	## append a trailing / if it's not there
	$dir .= '/' if($dir !~ /\/$/);
	my $dir_l1 = $dir.$lang1.'/';
	my $dir_l2 = $dir.$lang2.'/';
	print STDERR "$dir ... $dir_l1 ... $dir_l2\n";
	if (-d $dir_l1 && -d $dir_l2) {	
		for my $file1 (glob($dir_l1.'*.xml')) {
			$file1 = Encode::decode_utf8($file1);
			print "file::: \t", $file1,"\n";
			my $document1 = XML::Twig->new;
			if (! $document1->safe_parsefile ("$file1") ) {
				cluck "Parsing the XML-file failed: $file1";
			} else {
				my $location;
				my $root = $document1->root;
				my $header = $root->first_child('header');
				next if (!$header);
				my @parallel_texts = $header->children('parallel_text');
				foreach my $p (@parallel_texts) {
					if ($p->{'att'}->{'xml:lang'} eq $lang2) {
						#print $p->{'att'}->{'xml:lang'}, "\t";
						#print $p->{'att'}->{'location'}, "\n";
						$location = $p->{'att'}->{'location'};
						print "gogo_location: $location\n";
						last;
					}
					#				 else {
					#					 print "other parallel files: ", $p->{'att'}->{'xml:lang'}, "\t",	$p->{'att'}->{'location'}, "\n\n";
					#				 }
				}
				my $file2 =	$dir_l2.$location.".xml";
				$file2 = Encode::decode_utf8($file2);
				print "parallel file --- \t", $file2, "\n";
				my $document2 = XML::Twig->new;
				if (! $document2->safe_parsefile ("$file2") ) {
					cluck "Parsing the XML-file failed: $file2";
				} else {
					my $tca2_command = "java -Xms512m -Xmx1024m -jar dist/lib/alignment-20110210.jar -a $anchor_file $file1 $file2";
					print STDERR "$0: $tca2_command\n";
					if (system($tca2_command) != 0) { 
						next "errors in $tca2_command: $!\n"; 
					}
				}
			}
		}
	} else {
		print Encode::decode_utf8($dir_l1), " or ", Encode::decode_utf8($dir_l2), " ERROR: At least one of these directories doesn't exist.\n"; 
	}
} else { 
	print Encode::decode_utf8($dir), " ERROR: Directory doesn't exist.\n"; 
}
