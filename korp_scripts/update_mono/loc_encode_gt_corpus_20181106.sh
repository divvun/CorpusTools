#!/bin/sh

root_dir="/Users/car010/corpora"
cwb_dir="/usr/local/cwb-3.4.22"
corpus_data_dir="$root_dir/data"
registry_dir="$root_dir/registry"

input_data="$1"
date="$2"
descriptive_name="$3"
lang_code="$4"
l_corpus_name="$5"
#This works on the server, but not on Mac
#u_corpus_name=${l_corpus_name^^}
#This works on Mac
u_corpus_name=$(echo $l_corpus_name | tr '[:lower:]' '[:upper:]')
first_date="$6"
last_date="$7"


mkdir -vp $corpus_data_dir/$l_corpus_name
sent_nr=$(cat $input_data/$l_corpus_name.vrt|grep '<sentence'|wc -l)
cat > $corpus_data_dir/$l_corpus_name/.info << EOF
Sentences: $sent_nr
Updated: $date
FirstDate: $first_date
LastDate: $last_date

EOF

echo " ....... created $corpus_data_dir/$l_corpus_name/.info"

$cwb_dir/bin/cwb-encode -s -p - -d $corpus_data_dir/$l_corpus_name -R $registry_dir/$l_corpus_name -c utf8 -f $input_data/$l_corpus_name.vrt  -P word -P lemma -P pos -P msd -P ref -P deprel -P dephead -S sentence:0+id+token_count -S text:0+id+title+lang+orig_lang+gt_domain+first_name+last_name+nationality+date+datefrom+dateto+timefrom+timeto+sentence_count+token_count -S corpus:0+id

echo " ....... $l_corpus_name converted into the CWB binary format"
$cwb_dir/bin/cwb-makeall -r $registry_dir -D $u_corpus_name
echo " ....... created lexicon and index for p-attributes for $l_corpus_name"
$cwb_dir/bin/cwb-huffcode -r $registry_dir -A $u_corpus_name
echo " ....... compressed the token sequence of positional attributes for $l_corpus_name"
rm -fv $corpus_data_dir/$l_corpus_name/*.corpus
$cwb_dir/bin/cwb-compress-rdx -r $registry_dir -A $u_corpus_name
echo " ....... compressed the index of positional attributes for $l_corpus_name"
rm -fv $corpus_data_dir/$l_corpus_name/*.rev
rm -fv $corpus_data_dir/$l_corpus_name/*.rdx

if [ -f $registry_dir/$l_corpus_name ];
then
   echo "File $registry_dir/$l_corpus_name exists"
   name_placeholder='NAME ""'
   name_string='NAME "'$descriptive_name'"'
   lang_placeholder='language = "??"'
   lang_string='language = "'$lang_code'"'
   #This works on the server, but not on Mac
   #sed -i "s/${name_placeholder}/${name_string}/; s/${lang_placeholder}/${lang_string}/;" $registry_dir/$l_corpus_name
   #This works on Mac
   sed -i '' "s/${name_placeholder}/${name_string}/; s/${lang_placeholder}/${lang_string}/;" $registry_dir/$l_corpus_name
else
   echo "File $registry_dir/$l_corpus_name does not exists"
fi
