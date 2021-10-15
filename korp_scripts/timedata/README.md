# Steps to creat/update mysql tables for time data.

1. Extract time stamps from the vrt corpus
   Adjust `cLang, cDomain, date` variables in extract*time_stamp.xsl
   The script expects vrt file in folder `vrt_<cLang>_<date>`

2. Run the script
   `java -Xmx16800m -Dfile.encoding=UTF8 net.sf.saxon.Transform -it:main extract_time_stamp.xsl`
   If the above doesn't work specify the path to saxon9.jar
   `java -Xmx2048m -cp ~/main/tools/TermWikiExporter/lib/saxon9.jar -Dfile.encoding=UTF8 net.sf.saxon.Transform -it:main extract_time_stamp.xsl`
   output:
   `timestamp_<cLang>_<date>/metacheck_<cLang>_<cDomain>_<date>.txt`

3. Sort-uniq all extracted years
   `awk '{print \$2}' metacheck_<cLang>_<cDomain>_<date>.txt |s|u > all_years_<cLang>_<cDomain>.txt`

4. Adjust `lang, domain, date` variables in generate_tables.sh

5. Run the script
   `sh generate_tables.sh`
   output: `timespan_<cLang>_<cDomain>_<date>.sql`

6. Open `timespan_<cLang>_<cDomain>_<date>.sql` and replace `TESTCORPUS` by `<cLang>_<cDomain>_<date>` (in capitals)
   at `timespan_<cLang>_<cDomain>_<date>.sql`

7. Import timespan in mysql:
   `cat timespan_<cLang>_<cDomain>_<date>.sql | mysql -u korp -p korp_DB`
