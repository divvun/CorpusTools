#!/bin/bash

current_dir=`pwd`
#sme_4_server sme_4_server sme_4_server sme_4_server sme_4_server sme_4_server
#in_dir="korp_data_20181106_admin/"
#in_dir="test_admin/"
in_dir="sme/"

 echo "pwd $current_dir"
 #metaFile='loc_gt_metadata_20181106.json'
 #metaFile='loc_metadata_test.json'
 metaFile='loc_metadata_sme.json'

for f in $in_dir/*.vrt;
do
 echo "FILE: $f"
 file=$(basename $f)
 corpus_name="${file%.*}"
 echo "CN: $corpus_name"

 # https://stedolan.github.io/jq/manual/
 long_name=$(cat $metaFile | jq ".metadata.text[]|select(.id==\"${corpus_name}\")|.name")
 first_date=$(cat $metaFile | jq ".metadata.text[]|select(.id==\"${corpus_name}\")|.first_date")
 last_date=$(cat $metaFile | jq ".metadata.text[]|select(.id==\"${corpus_name}\")|.last_date")

 ln=$(eval echo $long_name)
 fd=$(eval echo $first_date)
 ld=$(eval echo $last_date)

 #echo "Name $n"
 #echo "First_date $f"
 #echo "Last_date $l"

input_data="$current_dir/$in_dir"
date="2021-06-25"
lang_code="sme"

sh loc_encode_gt_corpus_20181106.sh "$input_data" "$date" "$ln" "$lang_code" "$corpus_name" "$fd" "$ld"

done
