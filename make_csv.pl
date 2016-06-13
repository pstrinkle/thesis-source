#! /usr/bin/perl -w

# author: Patrick Trinkle
# date:   4/6/2011
# email:  tri1@umbc.edu
#
# usage: ./make_csv.pl tweets.xml > tweets.csv
#
# This takes the output from my tweet collection python.

(@ARGV == 1) or die "You need to also give it an input file.\n";

my $inputfile = shift;

open(IN, $inputfile) or die "Could not open: $inputfile\n";

my %months = ('Jan' => 1,
			  'Feb' => 2,
			  'Mar' => 3,
			  'Apr' => 4,
			  'May' => 5,
			  'Jun' => 6,
			  'Jul' => 7,
			  'Aug' => 8,
			  'Sep' => 9,
			  'Oct' => 10,
			  'Nov' => 11,
			  'Dec' => 12);

while (<IN>) {

	# <tweet><created>"Fri Feb 04 15:58:54 +0000 2011"</created><id>33555104208523264</id><source>"web"</source><text>"Delays  clear on I-495 in vicinity of earlier crash."</text></tweet>

    if ( m/<created>\"(\w{3}) (\w{3}) (\d{2}) (.*?) \+\d{4} (\d{4})\"<\/created>/i ) {

		$createdMonth = $2;
		$createdDay = $3;
		$createdTime = $4;
		$createdYear = $5;

		$datetime = $months{$createdMonth} . "/" . $createdDay . "/" . $createdYear . " " . $createdTime;

		if ( m/<text>\"(.*?)\"<\/text>/i ) {
			$text = $1;
		}

		print "\"" . $datetime . "\"" . "," . "\"" . $text . "\"" . "\n";
    }
}

close(IN);
