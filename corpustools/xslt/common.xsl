<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id$ -->

<!-- Format query results for display -->

<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:i18n="http://apache.org/cocoon/i18n/2.1"
    version="1.0">

    <xsl:output method="xml"
                version="1.0"
                encoding="UTF-8"
                indent="yes"
                doctype-public="-//UIT//DTD Corpus V1.0//EN"
                doctype-system="http://giellatekno.uit.no/dtd/corpus.dtd"/>


    <xsl:variable name="common_version" select="'$Revision$'"/>
    <xsl:variable name="convert2xml_version" select="''"/>
    <xsl:variable name="hyph_version" select="''"/>
    <xsl:variable name="xhtml2corpus_version" select="''"/>
    <xsl:variable name="docbook2corpus2_version" select="''"/>
    <xsl:param name="document_id" select="'no_id'"/>


    <!-- The following variables should be specified in the XSL -->
    <!-- template. They are added here, and kept in sync with   -->
    <!-- the DTD to avoid errors for old .xsl files.            -->
    <xsl:variable name="ocr" select="''"/>
    <xsl:variable name="note" select="''"/>
    <xsl:variable name="text_encoding" select="''"/>

    <xsl:variable name="mlangs">
    </xsl:variable>

    <xsl:variable name="parallels">
    </xsl:variable>

    <xsl:variable name="debug" select="false()"/>
    <xsl:variable name="nl" select="'&#xa;'"/>


    <!-- Fix empty em-type according to the dtd -->
    <xsl:template match="em">
        <xsl:element name="em">
            <xsl:choose>
                <xsl:when test="not(@type)">
                    <xsl:attribute name="type">
                        <xsl:text>italic</xsl:text>
                    </xsl:attribute>
                    <xsl:apply-templates/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:attribute name="type">
                        <xsl:value-of select="@type"/>
                    </xsl:attribute>
                    <xsl:apply-templates/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:element>
    </xsl:template>

    <!--
    <xsl:template match="p">
    <xsl:if test="string-length(normalize-space(.)) > 0">
    <xsl:apply-templates />
    </xsl:if>
    </xsl:template>
    -->


    <!-- Add all metadata from the xsl file to the resulting xml file: -->
    <xsl:template  match="document">
        <xsl:element name="document">
            <xsl:attribute name="xml:lang">
                <xsl:choose>
                    <xsl:when test="$mainlang">
                            <xsl:value-of select="$mainlang"/>
                    </xsl:when>
                    <xsl:when test="string-length(@xml:lang) = 0">
                            <xsl:value-of select="unknown"/>
                    </xsl:when>
                    <xsl:otherwise>
                            <xsl:value-of select="@xml:lang"/>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:attribute>

            <xsl:attribute name="id">
                <xsl:value-of select="$document_id"/>
            </xsl:attribute>

            <xsl:element name="header">
                <xsl:choose>
                    <xsl:when test="$title">
                        <xsl:element name="title">
                            <xsl:value-of select="$title"/>
                        </xsl:element>
                    </xsl:when>
                    <xsl:when test="header/title">
                        <xsl:apply-templates select="header/title"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:element name="title">
                        </xsl:element>
                    </xsl:otherwise>
                </xsl:choose>

                <xsl:choose>
                    <xsl:when test="$genre">
                        <xsl:element name="genre">
                            <xsl:attribute name="code">
                                <xsl:value-of select="$genre"/>
                            </xsl:attribute>
                        </xsl:element>
                    </xsl:when>
                    <xsl:when test="header/genre">
                        <xsl:apply-templates select="header/genre"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:element name="genre">
                        </xsl:element>
                    </xsl:otherwise>
                </xsl:choose>

                <!-- Only first author is tested from the original documents, others -->
                <!-- are just added -->
                <xsl:choose>
                    <xsl:when test="$author1_ln">
                        <xsl:element name="author">
                            <xsl:element name="person">
                            <xsl:attribute name="firstname">
                                <xsl:value-of select="$author1_fn"/>
                            </xsl:attribute>
                            <xsl:attribute name="lastname">
                                <xsl:value-of select="$author1_ln"/>
                            </xsl:attribute>
                            <xsl:attribute name="sex">
                                <xsl:value-of select="$author1_gender"/>
                            </xsl:attribute>
                            <xsl:attribute name="born">
                                <xsl:value-of select="$author1_born"/>
                            </xsl:attribute>
                            <xsl:attribute name="nationality">
                                <xsl:value-of select="$author1_nat"/>
                            </xsl:attribute>
                            </xsl:element>
                        </xsl:element>
                    </xsl:when>
                    <xsl:when test="header/author">
                        <xsl:apply-templates select="header/author"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:element name="author">
                                    <xsl:element name="unknown">
                                    </xsl:element>
                        </xsl:element>
                    </xsl:otherwise>
                </xsl:choose>

                <xsl:choose>
                    <xsl:when test="$author2_ln">
                        <xsl:element name="author">
                        <xsl:element name="person">
                            <xsl:attribute name="firstname">
                                <xsl:value-of select="$author2_fn"/>
                            </xsl:attribute>
                            <xsl:attribute name="lastname">
                                <xsl:value-of select="$author2_ln"/>
                            </xsl:attribute>
                            <xsl:attribute name="sex">
                                <xsl:value-of select="$author2_gender"/>
                            </xsl:attribute>
                            <xsl:attribute name="born">
                                <xsl:value-of select="$author2_born"/>
                            </xsl:attribute>
                            <xsl:attribute name="nationality">
                                <xsl:value-of select="$author2_nat"/>
                            </xsl:attribute>
                        </xsl:element>
                        </xsl:element>
                    </xsl:when>
                </xsl:choose>
                <xsl:choose>
                    <xsl:when test="$author3_ln">
                        <xsl:element name="author">
                        <xsl:element name="person">
                            <xsl:attribute name="firstname">
                                <xsl:value-of select="$author3_fn"/>
                            </xsl:attribute>
                            <xsl:attribute name="lastname">
                                <xsl:value-of select="$author3_ln"/>
                            </xsl:attribute>
                            <xsl:attribute name="sex">
                                <xsl:value-of select="$author3_gender"/>
                            </xsl:attribute>
                            <xsl:attribute name="born">
                                <xsl:value-of select="$author3_born"/>
                            </xsl:attribute>
                            <xsl:attribute name="nationality">
                                <xsl:value-of select="$author3_nat"/>
                            </xsl:attribute>
                        </xsl:element>
                        </xsl:element>
                    </xsl:when>
                </xsl:choose>
                <xsl:choose>
                    <xsl:when test="$author4_ln">
                        <xsl:element name="author">
                        <xsl:element name="person">
                            <xsl:attribute name="firstname">
                                <xsl:value-of select="$author4_fn"/>
                            </xsl:attribute>
                            <xsl:attribute name="lastname">
                                <xsl:value-of select="$author4_ln"/>
                            </xsl:attribute>
                            <xsl:attribute name="sex">
                                <xsl:value-of select="$author4_gender"/>
                            </xsl:attribute>
                            <xsl:attribute name="born">
                                <xsl:value-of select="$author4_born"/>
                            </xsl:attribute>
                            <xsl:attribute name="nationality">
                                <xsl:value-of select="$author4_nat"/>
                            </xsl:attribute>
                        </xsl:element>
                        </xsl:element>
                    </xsl:when>
                </xsl:choose>

                <!-- It is assumed that the translator does not come from
                outside, but is given only in this file -->
                <!-- There is a problem: how to test the existence of a
                translator that is not given here? -->
                <xsl:choose>
                    <xsl:when test="$translator_ln">
                        <xsl:element name="translator">
                            <xsl:element name="person">
                            <xsl:attribute name="firstname">
                                <xsl:value-of select="$translator_fn"/>
                            </xsl:attribute>
                            <xsl:attribute name="lastname">
                                <xsl:value-of select="$translator_ln"/>
                            </xsl:attribute>
                            <xsl:attribute name="sex">
                                <xsl:value-of select="$translator_gender"/>
                            </xsl:attribute>
                            <xsl:attribute name="born">
                                <xsl:value-of select="$translator_born"/>
                            </xsl:attribute>
                            <xsl:attribute name="nationality">
                                <xsl:value-of select="$translator_nat"/>
                            </xsl:attribute>
                            </xsl:element>
                        </xsl:element>
                    </xsl:when>
                    <xsl:when test="header/translator">
                        <xsl:apply-templates select="translator"/>
                    </xsl:when>
                    <xsl:when test="$translated_from or header/translated_from">
                        <xsl:element name="translator">
                                    <xsl:element name="unknown">
                                    </xsl:element>
                        </xsl:element>
                    </xsl:when>
                </xsl:choose>

                <xsl:choose>
                    <xsl:when test="$translated_from">
                        <xsl:element name="translated_from">
                        <xsl:attribute name="xml:lang">
                            <xsl:value-of select="$translated_from"/>
                        </xsl:attribute>
                        </xsl:element>
                    </xsl:when>
                    <xsl:otherwise>
                            <xsl:apply-templates select="header/translated_from"/>
                    </xsl:otherwise>
                </xsl:choose>

                <xsl:choose>
                    <xsl:when test="$year">
                        <xsl:element name="year">
                            <xsl:value-of select="$year"/>
                        </xsl:element>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:apply-templates select="header/year"/>
                    </xsl:otherwise>
                </xsl:choose>


                <xsl:choose>
                    <xsl:when test="$place">
                        <xsl:element name="place">
                            <xsl:value-of select="$place"/>
                        </xsl:element>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:apply-templates select="header/place"/>
                    </xsl:otherwise>
                </xsl:choose>

                <xsl:choose>
                    <xsl:when test="$publisher">
                        <xsl:element name="publChannel">
                            <xsl:element name="publication">
                                <xsl:element name="publisher">
                                    <xsl:value-of select="$publisher"/>
                                </xsl:element>
                                <xsl:choose>
                                    <xsl:when test="$ISSN">
                                    <xsl:element name="ISSN">
                                        <xsl:value-of select="$ISSN"/>
                                    </xsl:element>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:apply-templates select="header/ISSN"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                                <xsl:choose>
                                    <xsl:when test="$ISBN">
                                        <xsl:element name="ISBN">
                                            <xsl:value-of select="$ISBN"/>
                                        </xsl:element>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:apply-templates select="header/ISBN"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:element>
                        </xsl:element>
                    </xsl:when>
                    <xsl:when test="contains($publChannel, 'unpublished')">
                        <xsl:element name="publChannel">
                            <xsl:element name="unpublished">
                            </xsl:element>
                        </xsl:element>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:apply-templates select="header/publChannel"/>
                    </xsl:otherwise>
                </xsl:choose>


                <xsl:choose>
                    <xsl:when test="$collection">
                        <xsl:element name="collection">
                            <xsl:value-of select="$collection"/>
                        </xsl:element>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:apply-templates select="header/collection"/>
                    </xsl:otherwise>
                </xsl:choose>

                <xsl:choose>
                    <xsl:when test="$wordcount">
                        <xsl:element name="wordcount">
                            <xsl:value-of select="$wordcount"/>
                        </xsl:element>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:apply-templates select="header/wordcount"/>
                    </xsl:otherwise>
                </xsl:choose>

                <xsl:choose>
                    <xsl:when test="$ocr">
                        <xsl:element name="ocr"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:apply-templates select="header/ocr"/>
                    </xsl:otherwise>
                </xsl:choose>

                <xsl:choose>
                    <xsl:when test="$license_type">
                        <xsl:element name="availability">
                            <xsl:choose>
                                <xsl:when test="contains($license_type, 'free')">
                                    <xsl:element name="free">
                                    </xsl:element>
                                </xsl:when>
                                <xsl:when test="contract_id">
                                    <xsl:element name="license">
                                        <xsl:attribute name="type">
                                            <xsl:value-of select="$license_type"/>
                                        </xsl:attribute>
                                        <xsl:attribute name="contract_id">
                                            <xsl:value-of select="$contract_id"/>
                                        </xsl:attribute>
                                    </xsl:element>
                                </xsl:when>
                                <xsl:otherwise>
                                        <xsl:element name="license">
                                            <xsl:attribute name="type">
                                                <xsl:value-of select="$license_type"/>
                                            </xsl:attribute>
                                        </xsl:element>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:element>
                    </xsl:when>
                    <xsl:when test="header/availability">
                        <xsl:apply-templates select="header/availablity"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:element name="availability">
                            <xsl:element name="license">
                                <xsl:attribute name="type">
                                    <text>standard</text>
                                </xsl:attribute>
                            </xsl:element>
                        </xsl:element>
                    </xsl:otherwise>
                </xsl:choose>

                <xsl:if test="$sub_name or $sub_email">
                    <xsl:element name="submitter">
                        <xsl:if test="$sub_email">
                            <xsl:attribute name="name">
                                <xsl:value-of select="$sub_name"/>
                            </xsl:attribute>
                        </xsl:if>
                        <xsl:if test="$sub_email">
                            <xsl:attribute name="email">
                                <xsl:value-of select="$sub_email"/>
                            </xsl:attribute>
                        </xsl:if>
                    </xsl:element>
                </xsl:if>

                <xsl:choose>
                    <xsl:when test="$monolingual">
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:element name="multilingual">
                        </xsl:element>
                    </xsl:otherwise>
                </xsl:choose>

                <xsl:if test="$filename">
                    <xsl:element name="origFileName">
                        <xsl:value-of select="$filename"/>
                    </xsl:element>
                </xsl:if>

                <xsl:copy-of select="$parallels"/>

                <xsl:choose>
                    <xsl:when test="$metadata">
                        <xsl:element name="metadata">
                            <xsl:choose>
                                <xsl:when test="contains($metadata, 'uncomplete')">
                                    <xsl:element name="uncomplete">
                                    </xsl:element>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:element name="complete">
                                    </xsl:element>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:element>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:apply-templates select="header/metadata"/>
                    </xsl:otherwise>
                </xsl:choose>

                <xsl:element name="version">
                    <xsl:if test="$template_version">
                        <xsl:text>XSLtemplate </xsl:text>
                        <xsl:value-of select="$template_version"/>
                        <xsl:text>; </xsl:text>
                    </xsl:if>
                    <xsl:if test="$current_version">
                        <xsl:text>file-specific xsl  </xsl:text>
                        <xsl:value-of select="$current_version"/>
                        <xsl:text>; </xsl:text>
                    </xsl:if>
                    <xsl:if test="$common_version">
                        <xsl:text>common.xsl  </xsl:text>
                        <xsl:value-of select="$common_version"/>
                        <xsl:text>; </xsl:text>
                    </xsl:if>
                    <xsl:if test="$convert2xml_version">
                        <xsl:text>convert2xml  </xsl:text>
                        <xsl:value-of select="$convert2xml_version"/>
                        <xsl:text>; </xsl:text>
                    </xsl:if>
                    <xsl:if test="$hyph_version">
                        <xsl:text>add_hyph_tags  </xsl:text>
                        <xsl:value-of select="$hyph_version"/>
                        <xsl:text>; </xsl:text>
                    </xsl:if>
                    <xsl:if test="$docbook2corpus2_version">
                        <xsl:text>docbook2corpus2  </xsl:text>
                        <xsl:value-of select="$docbook2corpus2_version"/>
                        <xsl:text>; </xsl:text>
                    </xsl:if>
                    <xsl:if test="$xhtml2corpus_version">
                        <xsl:text>xhtml2corpus  </xsl:text>
                        <xsl:value-of select="$xhtml2corpus_version"/>
                        <xsl:text>; </xsl:text>
                    </xsl:if>
                </xsl:element>

                <xsl:if test="$note">
                    <xsl:element name="note">
                        <xsl:value-of select="$note"/>
                    </xsl:element>
                </xsl:if>


            </xsl:element>
            <xsl:apply-templates select="body"/>
        </xsl:element>
    </xsl:template>


    <!-- template for adding correct markup to the xml-file -->
    <!-- the target-string is searched from the file and replaced -->
    <!-- with "replacement" using error-correct -markup. -->

    <xsl:template name="globalCorrectMarkup">
        <xsl:param name="target"/>
        <xsl:param name="replacement"/>
        <xsl:param name="inputString"/>

        <xsl:choose>
            <xsl:when test="contains($inputString,$target)">
                <xsl:value-of select="substring-before($inputString,$target)"/>
                <xsl:element name="error">
                    <xsl:attribute name="correct">
                        <xsl:value-of select="$replacement"/>
                    </xsl:attribute>
                    <xsl:value-of select="$target"/>
                </xsl:element>
                <xsl:call-template name="globalCorrectMarkup">
                    <xsl:with-param name="inputString" select="substring-after($inputString,$target)"/>
                    <xsl:with-param name="target" select="$target"/>
                    <xsl:with-param name="replacement" select="$replacement"/>
                </xsl:call-template>
            </xsl:when>

            <xsl:otherwise>
                <xsl:value-of select="$inputString"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <!-- template for replacing strings in the text -->
    <!-- the text is gone through recursively -->
    <!-- the target and replacment strings are given as parameters -->
    <!-- separated by slash (/) -->
    <xsl:template name="globalTextReplace">

        <xsl:param name="continue"/>
        <xsl:param name="inputString"/>
        <xsl:param name="target"/>
        <xsl:param name="replacement"/>

        <xsl:variable name="OneTarget" select="substring-before($target,'/')"/>
        <xsl:variable name="OneReplacement" select="substring-before($replacement,'/')"/>

        <xsl:variable name="tmpTarget" select="substring-after($target,$OneTarget)"/>
        <xsl:variable name="tmpReplacement" select="substring-after($replacement,$OneReplacement)"/>

        <xsl:variable name="restTarget" select="substring($tmpTarget,2)"/>
        <xsl:variable name="restReplacement" select="substring($tmpReplacement,2)"/>

        <xsl:if test="$debug">
            <xsl:message terminate="no">
                <xsl:value-of select="concat('-----------------------------------------', $nl)"/>
                <xsl:value-of select="concat('input string |', $inputString, '|', $nl)"/>

                <xsl:value-of select="concat('OneTarget ss-before-slash-in-oneTarget |', $OneTarget, '|', $nl)"/>
                <xsl:value-of select="concat('OneReplacement ss-before-OneReplacement |', $OneReplacement, '|', $nl)"/>

                <xsl:value-of select="concat('tmpTarget ss-before-slash-in-tmpTarget |', $tmpTarget, '|', $nl)"/>
                <xsl:value-of select="concat('tmpReplacement ss-before-tmpReplacement |', $tmpReplacement, '|', $nl)"/>

                <xsl:value-of select="concat('restTarget ss-tmp_target-2 |', restTarget, '|', $nl)"/>
                <xsl:value-of select="concat('restReplacement ss-tmp_replacement-2 |', $restReplacement, '|', $nl)"/>

                <xsl:value-of select="'-----------------------------------------'"/>
            </xsl:message>
        </xsl:if>


        <!--
            <xsl:message>
            inputString <xsl:value-of select="$inputString"/>
            OneTarget <xsl:value-of select="$OneTarget"/>
            OneReplacement <xsl:value-of select="$OneReplacement"/>
            tmpTarget <xsl:value-of select="$OneTarget"/>
            tmpReplacement <xsl:value-of select="$OneReplacement"/>
            restTarget <xsl:value-of select="$restTarget"/>
            restReplacement <xsl:value-of select="$restReplacement"/>
            target <xsl:value-of select="$target"/>
            replacement <xsl:value-of select="$replacement"/>
            </xsl:message>
        -->

        <!-- when there is no more targets to test, the recursion ends here-->
        <xsl:choose>
            <xsl:when test="not(contains($tmpTarget,'/'))">
                <xsl:value-of select="$inputString"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:choose>
                    <!-- if a replacement was made, the search for the target continues at the -->
                    <!-- end of the string -->
                    <xsl:when test="$continue=1">
                        <xsl:choose>
                            <xsl:when test="contains($inputString, $OneTarget)">
                                <xsl:variable name="before" select="substring-before($inputString,$OneTarget)"/>
                                <xsl:variable name="after" select="substring-after($inputString,$OneTarget)"/>
                                <xsl:variable name="prefix" select="concat($before,$OneReplacement)"/>
                                <xsl:variable name="whole" select="concat($prefix,$after)"/>
                                <xsl:call-template name="globalTextReplace">
                                    <xsl:with-param name="continue" select="1"/>
                                    <xsl:with-param name="inputString" select="$whole"/>
                                    <xsl:with-param name="target" select="$target"/>
                                    <xsl:with-param name="replacement" select="$replacement"/>
                                </xsl:call-template>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:call-template name="globalTextReplace">
                                    <xsl:with-param name="continue" select="0"/>
                                    <xsl:with-param name="inputString" select="$inputString"/>
                                    <xsl:with-param name="target" select="$restTarget"/>
                                    <xsl:with-param name="replacement" select="$restReplacement"/>
                                </xsl:call-template>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:when>
                    <xsl:otherwise>

                        <!-- When the text is encountered first time, -->
                        <!-- the whole text is searched -->
                        <xsl:choose>
                            <xsl:when test="contains($inputString, $OneTarget)">
                                <xsl:variable name="before" select="substring-before($inputString,$OneTarget)"/>
                                <xsl:variable name="after" select="substring-after($inputString,$OneTarget)"/>
                                <xsl:variable name="prefix" select="concat($before,$OneReplacement)"/>
                                <xsl:variable name="whole" select="concat($prefix,$after)"/>

                                <xsl:call-template name="globalTextReplace">
                                    <xsl:with-param name="continue" select="1"/>
                                    <xsl:with-param name="inputString" select="$whole"/>
                                    <xsl:with-param name="target" select="$target"/>
                                    <xsl:with-param name="replacement" select="$replacement"/>
                                </xsl:call-template>
                            </xsl:when>
                            <xsl:otherwise>

                                <xsl:call-template name="globalTextReplace">
                                    <xsl:with-param name="continue" select="0"/>
                                    <xsl:with-param name="inputString" select="$inputString"/>
                                    <xsl:with-param name="target" select="$restTarget"/>
                                    <xsl:with-param name="replacement" select="$restReplacement"/>
                                </xsl:call-template>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <!-- Remove completely empty elements within the body: -->
    <xsl:template match="*[ancestor::body][not(node())]"/>

    <xsl:template match="node()|@*">
        <xsl:copy>
            <xsl:apply-templates select="node()|@*" />
        </xsl:copy>
    </xsl:template>

</xsl:stylesheet>
