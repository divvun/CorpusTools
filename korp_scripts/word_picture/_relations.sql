SET @@session.long_query_time = 1000;
DROP TABLE IF EXISTS `temp_relations_SME_ADMIN_20181106`;
CREATE TABLE `temp_relations_SME_ADMIN_20181106` (
   `id` int(11) NOT NULL DEFAULT 0,
   `head` int(11) NOT NULL DEFAULT 0,
   `rel` varchar(15) NOT NULL DEFAULT 'V',
   `dep` int(11) NOT NULL DEFAULT 0,
   `freq` int(11) NOT NULL DEFAULT 0,
   `bfhead` BOOL  NOT NULL,
   `bfdep` BOOL  NOT NULL,
   `wfhead` BOOL  NOT NULL,
   `wfdep` BOOL  NOT NULL,
 PRIMARY KEY (`head`, `wfhead`, `dep`, `rel`),
 INDEX `dep-wfdep-head-rel-freq-id` (`dep`, `wfdep`, `head`, `rel`, `freq`, `id`),
 INDEX `head-dep-bfhead-bfdep-rel-freq-id` (`head`, `dep`, `bfhead`, `bfdep`, `rel`, `freq`, `id`),
 INDEX `dep-head-bfhead-bfdep-rel-freq-id` (`dep`, `head`, `bfhead`, `bfdep`, `rel`, `freq`, `id`))  default charset = utf8  row_format = compressed ;
DROP TABLE IF EXISTS `temp_relations_SME_ADMIN_20181106_strings`;
CREATE TABLE `temp_relations_SME_ADMIN_20181106_strings` (
   `id` int(11) NOT NULL DEFAULT 0,
   `string` varchar(500) NOT NULL DEFAULT '',
   `stringextra` varchar(32) NOT NULL DEFAULT '',
   `pos` varchar(15) NOT NULL DEFAULT '',
   `lemma` varchar(500) NOT NULL DEFAULT '',
 PRIMARY KEY (`string`, `id`, `pos`, `stringextra`),
 INDEX `id-string-pos-stringextra` (`id`, `string`, `pos`, `stringextra`))  default charset = utf8  collate = utf8_bin  row_format = compressed ;
DROP TABLE IF EXISTS `temp_relations_SME_ADMIN_20181106_rel`;
CREATE TABLE `temp_relations_SME_ADMIN_20181106_rel` (
   `rel` varchar(15) NOT NULL DEFAULT 'V',
   `freq` int(11) NOT NULL DEFAULT 0,
 PRIMARY KEY (`rel`))  default charset = utf8  collate = utf8_bin  row_format = compressed ;
DROP TABLE IF EXISTS `temp_relations_SME_ADMIN_20181106_head_rel`;
CREATE TABLE `temp_relations_SME_ADMIN_20181106_head_rel` (
   `head` int(11) NOT NULL DEFAULT 0,
   `rel` varchar(15) NOT NULL DEFAULT 'V',
   `freq` int(11) NOT NULL DEFAULT 0,
 PRIMARY KEY (`head`, `rel`))  default charset = utf8  collate = utf8_bin  row_format = compressed ;
DROP TABLE IF EXISTS `temp_relations_SME_ADMIN_20181106_dep_rel`;
CREATE TABLE `temp_relations_SME_ADMIN_20181106_dep_rel` (
   `dep` int(11) NOT NULL DEFAULT 0,
   `rel` varchar(15) NOT NULL DEFAULT 'V',
   `freq` int(11) NOT NULL DEFAULT 0,
 PRIMARY KEY (`dep`, `rel`))  default charset = utf8  collate = utf8_bin  row_format = compressed ;
DROP TABLE IF EXISTS `temp_relations_SME_ADMIN_20181106_sentences`;
CREATE TABLE `temp_relations_SME_ADMIN_20181106_sentences` (
   `id` int(11)  DEFAULT NULL,
   `sentence` varchar(64) NOT NULL DEFAULT '',
   `start` int(11)  DEFAULT NULL,
   `end` int(11)  DEFAULT NULL,
 INDEX `id` (`id`))  default charset = utf8  collate = utf8_bin  row_format = compressed ;
ALTER TABLE `temp_relations_SME_ADMIN_20181106` DISABLE KEYS;
ALTER TABLE `temp_relations_SME_ADMIN_20181106_strings` DISABLE KEYS;
ALTER TABLE `temp_relations_SME_ADMIN_20181106_rel` DISABLE KEYS;
ALTER TABLE `temp_relations_SME_ADMIN_20181106_head_rel` DISABLE KEYS;
ALTER TABLE `temp_relations_SME_ADMIN_20181106_dep_rel` DISABLE KEYS;
ALTER TABLE `temp_relations_SME_ADMIN_20181106_sentences` DISABLE KEYS;
SET FOREIGN_KEY_CHECKS = 0;
SET UNIQUE_CHECKS = 0;
SET AUTOCOMMIT = 0;
SET NAMES utf8;
ALTER TABLE `temp_relations_SME_ADMIN_20181106` ENABLE KEYS;
ALTER TABLE `temp_relations_SME_ADMIN_20181106_strings` ENABLE KEYS;
ALTER TABLE `temp_relations_SME_ADMIN_20181106_rel` ENABLE KEYS;
ALTER TABLE `temp_relations_SME_ADMIN_20181106_head_rel` ENABLE KEYS;
ALTER TABLE `temp_relations_SME_ADMIN_20181106_dep_rel` ENABLE KEYS;
ALTER TABLE `temp_relations_SME_ADMIN_20181106_sentences` ENABLE KEYS;
DROP TABLE IF EXISTS `relations_SME_ADMIN_20181106`, `relations_SME_ADMIN_20181106_strings`, `relations_SME_ADMIN_20181106_rel`, `relations_SME_ADMIN_20181106_head_rel`, `relations_SME_ADMIN_20181106_dep_rel`, `relations_SME_ADMIN_20181106_sentences`;
RENAME TABLE `temp_relations_SME_ADMIN_20181106` TO `relations_SME_ADMIN_20181106`, `temp_relations_SME_ADMIN_20181106_strings` TO `relations_SME_ADMIN_20181106_strings`, `temp_relations_SME_ADMIN_20181106_rel` TO `relations_SME_ADMIN_20181106_rel`, `temp_relations_SME_ADMIN_20181106_head_rel` TO `relations_SME_ADMIN_20181106_head_rel`, `temp_relations_SME_ADMIN_20181106_dep_rel` TO `relations_SME_ADMIN_20181106_dep_rel`, `temp_relations_SME_ADMIN_20181106_sentences` TO `relations_SME_ADMIN_20181106_sentences`;
SET UNIQUE_CHECKS = 1;
SET FOREIGN_KEY_CHECKS = 1;
COMMIT;
