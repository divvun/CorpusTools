#!/bin/bash

current_dir=`pwd`
lang_code='nob'
plang_code='smj'
in_dir="nob2smj_20210929"

echo "pwd $current_dir"
metaFile='gt_metadata_parallel_corpus_smj.json'

for f_plang in $in_dir/*-${plang_code}.vrt;
do
  sed -i '' 's/^ *//' $f_plang
done

for f in $in_dir/*-${lang_code}.vrt;
do
 echo "FILE: $f"
 sed -i '' 's/^ *//' $f
 file=$(basename $f)
 corpus_name="${file%.*}"
 pcorpus_name="${file%-*}-$plang_code"
 echo "CN: $corpus_name"
 echo "PCN: $pcorpus_name"

 # https://stedolan.github.io/jq/manual/
 long_name=$(cat $metaFile | jq ".metadata.text[]|select(.id==\"${corpus_name}\")|.name")
 echo "long_name: $long_name"
# first_date=$(cat $metaFile | jq ".metadata.text[]|select(.id==\"${corpus_name}\")|.first_date")
# last_date=$(cat $metaFile | jq ".metadata.text[]|select(.id==\"${corpus_name}\")|.last_date")

 ln=$(eval echo $long_name)
# fd=$(eval echo $first_date)
# ld=$(eval echo $last_date)

 fd='0000-00-00 00:00:00'
 ld='0000-00-00 00:00:00'

 echo "Name $ln"
 echo "First_date $fd"
 echo "Last_date $ld"

input_data="$current_dir/$in_dir"
date="2021-09-29"

sh encode_gt_corpus.sh "$input_data" "$date" "$ln" "$lang_code" "$corpus_name" "$fd" "$ld"
sh encode_gt_corpus.sh "$input_data" "$date" "$ln" "$plang_code" "$pcorpus_name" "$fd" "$ld"
sh align_files.sh $corpus_name $pcorpus_name

done
