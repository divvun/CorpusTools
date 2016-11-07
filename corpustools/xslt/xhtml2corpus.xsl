<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:html="http://www.w3.org/1999/xhtml"
                xmlns:svg="http://www.w3.org/2000/svg"
                xmlns:saxon="http://icl.com/saxon"
                xmlns:str="http://exslt.org/strings"
                extension-element-prefixes="str"
                exclude-result-prefixes="xsl fo html saxon svg">
<!--$Revision: 38657 $ -->

<!--
Usage: ~/Desktop/bin/tidy - -quote-nbsp no - -add-xml-decl yes
                        - -enclose-block-text yes -asxml -utf8 -language sme
                        file.html |
xsltproc xhtml2corpus.xsl - > file.xml
-->

<xsl:strip-space elements="*"/>

<xsl:output method="xml"
           version="1.0"
           encoding="UTF-8"
           indent="yes"
           doctype-public="-//UIT//DTD Corpus V1.0//EN"
           doctype-system="http://www.giellatekno.uit.no/dtd/corpus.dtd"/>

<!-- Main block-level conversions -->
<xsl:template match="html">
    <document>
        <xsl:apply-templates select="head"/>
        <xsl:apply-templates select="body"/>
    </document>
</xsl:template>

<xsl:template match="head">
    <header>
        <title>
            <xsl:choose>
                <xsl:when test="title">
                        <xsl:value-of select="title"/>
                </xsl:when>
            </xsl:choose>
        </title>
    </header>
</xsl:template>

<xsl:template match="body">
    <body>
        <xsl:apply-templates />
    </body>
</xsl:template>


<!-- This template matches on all HTML header items and makes them into
     bridgeheads. It attempts to assign an ID to each bridgehead by looking
     for a named anchor as a child of the header or as the immediate preceding
     or following sibling -->
<xsl:template match="h1|
              h2|
              h3|
              h4|
              h5|
              h6">
    <xsl:if test="string-length(normalize-space(.)) > 1">
        <xsl:choose>
            <xsl:when test="ancestor::li">
                <span><xsl:apply-templates/></span>
            </xsl:when>
            <xsl:otherwise>
                <p type="title">
                    <xsl:value-of select="."/>
                </p>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:if>
</xsl:template>

<xsl:template match="p|
              label">
    <xsl:if test="string-length(normalize-space(.)) > 1">
        <xsl:choose>
            <xsl:when test="ancestor::i|
                      ancestor::u|
                      ancestor::b|
                      ancestor::p|
                      ancestor::li|
                      ancestor::span|
                      */ol|
                      */ul">
                <xsl:apply-templates />
            </xsl:when>
            <xsl:when test="contains(., '•')">
                <xsl:for-each select="str:tokenize(., '•')">
                    <p type="listitem">
                        <xsl:value-of select="."/>
                    </p>
                </xsl:for-each>
            </xsl:when>
            <xsl:otherwise>
                <p>
                    <xsl:apply-templates />
                </p>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:if>
</xsl:template>

<xsl:template match="pre">
    <pre>
        <xsl:apply-templates/>
    </pre>
</xsl:template>

<!-- LIST ELEMENTS -->

<xsl:template match="ol|
              ul">
    <list>
        <xsl:apply-templates select="*"/>
    </list>
</xsl:template>

<xsl:template match="ul/strong">
    <xsl:choose>
        <xsl:when test="text()">
            <p>
                <xsl:apply-templates/>
            </p>
        </xsl:when>
        <xsl:otherwise>
            <xsl:apply-templates/>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="li">
    <xsl:choose>
        <xsl:when test="div/p">
            <xsl:for-each select="div/p">
                <p type="listitem">
                    <xsl:value-of select="."/>
                </p>
            </xsl:for-each>
        </xsl:when>
        <xsl:when test="p/i">
            <p type="listitem">
                <xsl:apply-templates/>
            </p>
        </xsl:when>
        <xsl:otherwise>
            <p type="listitem">
                <xsl:apply-templates select="*|text()"/>
            </p>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<!-- This template makes a DocBook variablelist out of an HTML definition list -->
<xsl:template match="dl">
    <xsl:for-each select="dt">
        <p type="listitem">
            <xsl:apply-templates/>
        </p>
        <xsl:apply-templates select="following-sibling::dd"/>
    </xsl:for-each>
</xsl:template>

<xsl:template match="dd">
    <xsl:choose>
        <xsl:when test="p">
            <xsl:apply-templates/>
        </xsl:when>
        <xsl:otherwise>
            <p>
                <xsl:apply-templates/>
            </p>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="center">
    <xsl:if test="string-length(normalize-space(.)) > 1">
        <p>
            <xsl:value-of select="text()"/>
        </p>
    </xsl:if>
</xsl:template>

<xsl:template match="dato">
    <xsl:value-of select="text()"/>
</xsl:template>


<!-- inline formatting -->
<xsl:template match="b">
    <xsl:choose>
        <xsl:when test="ancestor::b|
                        ancestor::i|
                        ancestor::em|
                        u|
                        ancestor::h2">
            <xsl:apply-templates/>
        </xsl:when>
        <xsl:when test="ancestor::p|
                        ancestor::div|
                        ancestor::li|
                        ancestor::td|
                        parent::p|
                        parent::font|
                        parent::span">
            <em type="bold">
                <xsl:apply-templates/>
            </em>
        </xsl:when>
        <!-- If the above tests are correct and all failed, then we
             have no ancestor that could have added a <p>: -->
        <xsl:otherwise>
            <p>
                <em type="bold">
                    <xsl:apply-templates/>
                </em>
            </p>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="div/b|td/b">
    <p>
        <em type="bold">
            <xsl:apply-templates/>
        </em>
    </p>
</xsl:template>

<xsl:template match="i|
              em|
              u|
              strong">
    <xsl:choose>
        <xsl:when test="ancestor::strong|
                  ancestor::b|
                  ancestor::i|
                  ancestor::em|
                  ancestor::u|
                  ol|
                  ul">
            <xsl:apply-templates/>
        </xsl:when>
        <xsl:when test="ancestor::li">
            <em><xsl:apply-templates/></em>
        </xsl:when>
        <xsl:when test="not(ancestor::p|
                  ancestor::a|
                  ancestor::h1|
                  ancestor::h2|
                  ancestor::h3|
                  ancestor::h4|
                  ancestor::li)">
            <em type="bold">
                <xsl:apply-templates/>
            </em>
        </xsl:when>
        <xsl:when test="b">
            <xsl:apply-templates/>
        </xsl:when>
        <xsl:otherwise>
            <em type="italic">
                <xsl:apply-templates/>
            </em>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="div/i|
              td/i">
    <p>
        <em type="italic">
            <xsl:apply-templates/>
        </em>
    </p>
</xsl:template>

<xsl:template match="div/em|
              td/em">
    <xsl:choose>
        <xsl:when test="p">
            <xsl:apply-templates/>
        </xsl:when>
        <xsl:otherwise>
            <p>
                <em>
                    <xsl:apply-templates/>
                </em>
            </p>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="p/a/div">
    <xsl:value-of select="text()"/>
</xsl:template>

<xsl:template match="div/u|
              td/u|
              div/strong|
              td/strong">
    <p>
        <em type="bold">
            <xsl:apply-templates/>
        </em>
    </p>
</xsl:template>

<xsl:template match="td/a/p|
              div/a/p">
    <xsl:apply-templates />
</xsl:template>

<!-- Table formatting -->
<xsl:template match="tbody">
    <xsl:apply-templates />
</xsl:template>

<xsl:template match="table">
    <xsl:apply-templates />
</xsl:template>

<xsl:template match="pb">
    <xsl:apply-templates />
</xsl:template>

<!--
A td can either behave as a container or a p like element.
If it is a container it has one or more of the these tags:
* p, hX, table, div (just apply-templates)
* otherwise, add <p> around the content of td
-->
<xsl:template match="td">
    <xsl:apply-templates/>
</xsl:template>

<!--
A div can either behave as a container or a p like element.
If it is a container it has one or more of the these tags:
* p, hX, table, div (just apply-templates)
* otherwise, add <p> around the content of td
-->
<xsl:template match="div">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="thead">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="caption|
              th">
    <xsl:choose>
        <xsl:when test="div|
                  ancestor::p|
                  ancestor::b|
                  ancestor::i|
                  ancestor::u|
                  ancestor::a|
                  p|
                  b">
            <xsl:apply-templates/>
        </xsl:when>
        <xsl:otherwise>
            <p>
                <xsl:apply-templates/>
            </p>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="tr">
    <xsl:apply-templates />
</xsl:template>

<!-- references -->
<xsl:template match="a">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="div/a|
              td/a">
    <xsl:choose>
        <xsl:when test="h2|
                  div">
            <xsl:apply-templates/>
        </xsl:when>
        <xsl:otherwise>
            <p>
                <xsl:apply-templates/>
            </p>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="div/text()|
              td/text()|
              div/abbr">
    <p>
        <xsl:value-of select="."/>
    </p>
</xsl:template>

<xsl:template match="li//div">
    <xsl:value-of select="text()"/>
</xsl:template>

<xsl:template match="form|
              input">
    <xsl:apply-templates/>
</xsl:template>

<!-- quotations -->
<xsl:template match="q">
    <xsl:apply-templates />
</xsl:template>

<xsl:template match="blockquote">
    <p>
        <span type="quote">
            <xsl:value-of select="."/>
        </span>
    </p>
</xsl:template>

<!-- superscripts and subscripts are dropped to text -->
<xsl:template match="sub|
              sup">
    <xsl:choose>
        <xsl:when test="text()">
            <xsl:choose>
                <xsl:when test="ancestor::p|
                          ancestor::b|
                          ancestor::i|
                          ancestor::u|
                          ancestor::a|
                          ancestor::font|
                          ancestor::li|
                          ancestor::span">
                    <xsl:apply-templates select="text()"/>
                </xsl:when>
                <xsl:otherwise>
                    <p><xsl:apply-templates select="text()"/></p>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:when>
        <xsl:otherwise>
            <xsl:apply-templates/>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="small">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="span">
    <xsl:apply-templates/><xsl:text> </xsl:text>
</xsl:template>

<xsl:template match="div/span|
              td/span">
    <p>
        <xsl:apply-templates/>
    </p>
</xsl:template>

<!-- other formatting -->
<xsl:template match="note">
    <xsl:choose>
        <xsl:when test="text()">
            <xsl:choose>
                <xsl:when test="ancestor::p|
                          ancestor::b|
                          ancestor::i|
                          ancestor::u|
                          ancestor::a|
                          ancestor::dt|
                          ancestor::h1|
                          ancestor::h2|
                          ancestor::h3|
                          ancestor::h4|
                          ancestor::strong|
                          ancestor::span|
                          ancestor::li">
                    <xsl:apply-templates/><xsl:text> </xsl:text>
                </xsl:when>
                <xsl:otherwise>
                    <p><xsl:apply-templates/></p>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:when>
        <xsl:otherwise>
            <xsl:apply-templates/>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="font">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="ol/i">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="div/font|
              td/font">
    <xsl:choose>
        <xsl:when test="ancestor::em|
                  font|
                  p">
            <xsl:apply-templates/>
        </xsl:when>
        <xsl:otherwise>
            <p>
                <xsl:apply-templates/>
            </p>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="pb">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="title">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="nobr">
    <p>
        <xsl:apply-templates/>
    </p>
</xsl:template>

<xsl:template match="header">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="text()">
    <xsl:value-of select="normalize-space(.)"/><xsl:text> </xsl:text>
</xsl:template>

<xsl:template match="textarea">
    <p>
        <xsl:apply-templates />
    </p>
</xsl:template>

<xsl:template match="big">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="*">
    <xsl:message>No template for <xsl:value-of select="name()"/>
        <xsl:text>: </xsl:text><xsl:value-of select="text()"/>
    </xsl:message>
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="@*">
    <xsl:message>No template for attribute <xsl:value-of select="name()"/>
        <xsl:text>: </xsl:text><xsl:value-of select="text()"/>
    </xsl:message>
    <xsl:apply-templates/>
</xsl:template>

<!-- Ignored elements -->
<xsl:template match="br"/>
<xsl:template match="wbr"/>
<xsl:template match="colgroup"/>
<xsl:template match="svg:svg"/>

</xsl:stylesheet>

