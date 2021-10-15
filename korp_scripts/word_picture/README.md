# Steps to creat/update mysql tables for word picture.
Skip step 0 if korp database and korp user already exist.

0. Create korp database korp_DB, create the user korp and grant all access to database
`mysql -u root -p`
In mysql shell run:
`CREATE DATABASE korp_DB character set utf8 collate utf8_bin;`
`CREATE USER 'korp'@'localhost' IDENTIFIED BY <password>`
`GRANT ALL ON korp_DB.* TO korp@localhost;`
NB. The names for database, user and password are the same in settings_not_in_svn.py (see point 2)

1. Create/reset tables in korp_DB
`mysql -u root -p`
NB. First replace corpus name as needed in `_relations.sql`, i.e. replace "SME_ADMIN_20181106".
In mysql shell run:
`source ~/main/apps/korp/word_picture/_relations.sql`

2. Fill mysql tables
NB. All paths and password are stored in settings_not_in_svn.py, which is not in svn!
Copy settings_not_in_svn.template to settings_not_in_svn.py and replace paths and passwords as needed.
`python insert.py`
NB. In the current version, the script will fill tables with strings and relations present in corpus.
It is possible to search for both base forms and word forms, but results are collected by base form.
This means that if "lean" is the search word (which has base form "leat"), all relations for word forms with lemma "leat" are presented.
The results are always displayed as base forms (same as for the swedish version).

3. Whenever corpus/tables update run:
`rm -rf /tmp/gt_korp_2018_WSGI/*`
If error `bash: /bin/rm: Argument list too long`, run the following:
`find /tmp/gt_korp_2018_WSGI/ -type f -delete`
