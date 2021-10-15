#!/bin/sh

# ${string,,} toLower
# ${string^^} toUpper
# ${string,,[AEIUO]}
# ${string^^[aeiou]}

#l_corpus_name="sms_wikipedia_20161208"
#u_corpus_name=${l_corpus_name^^}

lang="smj"
ulang=$(echo $lang | tr '[a-z]' '[A-Z]')
domain="science"
udomain=$(echo $domain | tr '[a-z]' '[A-Z]')
date="20210520"
metafile="timestamp_"${lang}"_"${date}"/metacheck_"${lang}"_"${domain}"_"${date}".txt"
db=${ulang}"_"${udomain}"_"${date}
ylist='all_years_'${ulang}'_'${udomain}'.txt'
target="timespan_${lang}_${domain}_${date}.sql"

cp form_timespan.sql $target

#sed -i 's/TESTCORPUS/${db}/g' $target

awk '{print $2}' $metafile |sort|uniq> $ylist

for y in $(cat $ylist)
do
 echo "year is $y"
 year=$(echo $y |cut -c 1-4)
 sum=$(grep "^$y" $metafile|awk '{count=count+$NF}END{print count}')
 echo "INSERT INTO \`timedata\` (corpus, datefrom, dateto, tokens) VALUES">>$target
 echo "('${db}', '${year}0101000000', '${year}1231235959', $sum);">>$target
 echo "INSERT INTO \`timedata_date\` (corpus, datefrom, dateto, tokens) VALUES">>$target
 echo "('${db}', '${year}0101', '${year}1231', $sum);">>$target
 echo "==============="
done
