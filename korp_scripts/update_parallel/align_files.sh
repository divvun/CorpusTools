#!/bin/sh

#Comment ln 4-5 if running on the server
root_dir="/Users/car010/corpora"
cwb_dir="/usr/local/cwb-3.4.22"
#Uncomment ln 7-8 if running on the server
#root_dir="/corpora/gt_cwb/"
#cwb_dir="/usr/local/cwb-3.4.15"

data="$root_dir/data"
registry="$root_dir/registry"
c1="$1"
c2="$2"

$cwb_dir/bin/cwb-align -r $registry -v -o $data/$c1/$c1.align -V link_id $c1 $c2 link
$cwb_dir/bin/cwb-align -r $registry -v -o $data/$c2/$c2.align -V link_id $c2 $c1 link
#fin2smn 2017
#$cwb_dir/bin/cwb-align -r $registry -v -o $data/$c2/$c2.align -V sentence_id $c1 $c2 sentence
#$cwb_dir/bin/cwb-align -r $registry -v -o $data/$c2/$c2.align -V sentence_id $c2 $c1 sentence


$cwb_dir/bin/cwb-align-encode -r $registry -v -d $data/$c1/ $data/$c1/$c1.align
$cwb_dir/bin/cwb-align-encode -r $registry -v -d $data/$c2/ $data/$c2/$c2.align


cat >> $registry/$c1 << EOF
ALIGNED $c2

EOF

cat >> $registry/$c2 << EOF
ALIGNED $c1

EOF
