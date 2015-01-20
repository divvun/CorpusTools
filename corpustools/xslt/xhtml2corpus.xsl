<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:html="http://www.w3.org/1999/xhtml"
                xmlns:saxon="http://icl.com/saxon"
                xmlns:str="http://exslt.org/strings"
                extension-element-prefixes="str"
                exclude-result-prefixes="xsl fo html saxon">
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
<xsl:template match="html:html">
    <document>
        <xsl:apply-templates select="html:head"/>
        <xsl:apply-templates select="html:body"/>
    </document>
</xsl:template>

<xsl:template match="html:head">
    <header>
        <title>
            <xsl:choose>
                <xsl:when test="html:title">
                        <xsl:value-of select="html:title"/>
                </xsl:when>
            </xsl:choose>
        </title>
    </header>
</xsl:template>

<xsl:template match="html:body">
    <body>
        <xsl:apply-templates />
    </body>
</xsl:template>


<!-- This template matches on all HTML header items and makes them into
     bridgeheads. It attempts to assign an ID to each bridgehead by looking
     for a named anchor as a child of the header or as the immediate preceding
     or following sibling -->
<xsl:template match="html:h1
              |html:h2
              |html:h3
              |html:h4
              |html:h5
              |html:h6">
    <xsl:if test="string-length(normalize-space(.)) > 1">
        <xsl:choose>
            <xsl:when test="ancestor::html:li">
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

<xsl:template match="html:p|html:label">
    <xsl:if test="string-length(normalize-space(.)) > 1">
        <xsl:choose>
            <xsl:when test="ancestor::html:i|ancestor::html:u|ancestor::html:b|ancestor::html:p|ancestor::html:li|ancestor::html:span">
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

<xsl:template match="html:pre">
    <pre>
        <xsl:apply-templates/>
    </pre>
</xsl:template>

<!-- LIST ELEMENTS -->

<xsl:template match="html:ol|html:ul">
    <list>
        <xsl:apply-templates select="*"/>
    </list>
</xsl:template>

<xsl:template match="html:ul/html:strong">
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

<xsl:template match="html:li">
    <xsl:choose>
        <xsl:when test="html:div/html:p">
            <xsl:for-each select="html:div/html:p">
                <p type="listitem">
                    <xsl:value-of select="."/>
                </p>
            </xsl:for-each>
        </xsl:when>
        <xsl:when test="html:p/html:i">
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
<xsl:template match="html:dl">
    <xsl:for-each select="html:dt">
        <p type="listitem">
            <xsl:apply-templates/>
        </p>
        <xsl:apply-templates select="following-sibling::html:dd"/>
    </xsl:for-each>
</xsl:template>

<xsl:template match="html:dd">
    <xsl:choose>
        <xsl:when test="html:p">
            <xsl:apply-templates/>
        </xsl:when>
        <xsl:otherwise>
            <p>
                <xsl:apply-templates/>
            </p>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="html:center">
    <xsl:if test="string-length(normalize-space(.)) > 1">
        <p >
            <xsl:value-of select="text()"/>
        </p>
    </xsl:if>
</xsl:template>

<xsl:template match="html:dato">
    <xsl:value-of select="text()"/>
</xsl:template>


<!-- inline formatting -->
<xsl:template match="html:b">
    <xsl:choose>
        <xsl:when test="ancestor::html:b|
                        ancestor::html:i|
                        ancestor::html:em|
                        html:u|
                        ancestor::html:h2">
            <xsl:apply-templates/>
        </xsl:when>
        <xsl:when test="ancestor::html:p|ancestor::html:li|ancestor::html:td">
            <em type="bold">
                <xsl:apply-templates/>
            </em>
        </xsl:when>
        <xsl:when test="parent::html:p|parent::html:font|parent::html:span">
            <em type="bold">
                <xsl:apply-templates/>
            </em>
        </xsl:when>

        <xsl:otherwise>
            <p>
                <em type="bold">
                    <xsl:apply-templates/>
                </em>
            </p>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="html:div/html:b|html:td/html:b">
    <p>
        <em type="bold">
            <xsl:apply-templates/>
        </em>
    </p>
</xsl:template>

<xsl:template match="html:i|html:em|html:u|html:strong">
    <xsl:choose>
        <xsl:when test="ancestor::html:strong|ancestor::html:b|ancestor::html:i|ancestor::html:em|ancestor::html:u">
            <xsl:apply-templates/>
        </xsl:when>
        <xsl:when test="ancestor::html:li">
            <em><xsl:apply-templates/></em>
        </xsl:when>
        <xsl:when test="not(ancestor::html:p|ancestor::html:a|ancestor::html:h1|ancestor::html:h2|ancestor::html:h3|ancestor::html:h4|ancestor::html:li)">
            <em type="bold">
                <xsl:apply-templates/>
            </em>
        </xsl:when>
        <xsl:otherwise>
            <em type="italic">
                <xsl:apply-templates/>
            </em>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="html:div/html:i|html:td/html:i">
    <p>
        <em type="italic">
            <xsl:apply-templates/>
        </em>
    </p>
</xsl:template>

<xsl:template match="html:div/html:em|html:td/html:em">
    <xsl:choose>
        <xsl:when test="html:p">
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

<xsl:template match="html:p/html:a/html:div">
    <xsl:value-of select="text()"/>
</xsl:template>

<xsl:template match="html:div/html:u|html:td/html:u|html:div/html:strong|html:td/html:strong">
    <p>
        <em type="bold">
            <xsl:apply-templates/>
        </em>
    </p>
</xsl:template>

<xsl:template match="html:td/html:a/html:p|html:div/html:a/html:p">
    <xsl:apply-templates />
</xsl:template>

<xsl:template match="html:address">
    <p>
        <xsl:apply-templates/>
    </p>
</xsl:template>

<!-- Table formatting -->
<xsl:template match="html:tbody">
    <xsl:apply-templates />
</xsl:template>

<xsl:template match="html:table">
    <xsl:apply-templates />
</xsl:template>

<xsl:template match="html:pb">
    <xsl:apply-templates />
</xsl:template>

<!--
A td can either behave as a container or a p like element.
If it is a container it has one or more of the these tags:
* p, hX, table, div (just apply-templates)
* otherwise, add <p> around the content of td
-->
<xsl:template match="html:td">
    <xsl:apply-templates/>
</xsl:template>

<!--
A div can either behave as a container or a p like element.
If it is a container it has one or more of the these tags:
* p, hX, table, div (just apply-templates)
* otherwise, add <p> around the content of td
-->
<xsl:template match="html:div">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="html:thead">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="html:caption|html:th">
    <xsl:choose>
        <xsl:when test="html:div|ancestor::html:p|ancestor::html:b|ancestor::html:i|ancestor::html:u|ancestor::html:a|html:p|html:b">
            <xsl:apply-templates/>
        </xsl:when>
        <xsl:otherwise>
            <p>
                <xsl:apply-templates/>
            </p>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="html:tr">
    <xsl:apply-templates />
</xsl:template>

<!-- references -->
<xsl:template match="html:a">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="html:div/html:a|html:td/html:a">
    <xsl:choose>
        <xsl:when test="html:h2|html:div">
            <xsl:apply-templates/>
        </xsl:when>
        <xsl:otherwise>
            <p>
                <xsl:apply-templates/>
            </p>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="html:div/text()|html:td/text()|html:div/html:abbr">
    <p>
        <xsl:value-of select="."/>
    </p>
</xsl:template>

<xsl:template match="html:li//html:div">
    <xsl:value-of select="text()"/>
</xsl:template>

<xsl:template match="html:form|html:input">
    <xsl:apply-templates/>
</xsl:template>

<!-- quotations -->
<xsl:template match="html:q">
    <xsl:apply-templates />
</xsl:template>

<xsl:template match="html:blockquote">
    <p>
        <span type="quote">
            <xsl:value-of select="."/>
        </span>
    </p>
</xsl:template>

<!-- superscripts and subscripts are dropped to text -->
<xsl:template match="html:big|html:small|html:sub|html:sup">
    <xsl:choose>
        <xsl:when test="text()">
            <xsl:choose>
                <xsl:when test="ancestor::html:p|ancestor::html:b|ancestor::html:i|ancestor::html:u|ancestor::html:a|ancestor::html:font|ancestor::html:li">
                    <xsl:apply-templates select="text()"/>
                </xsl:when>
                <xsl:otherwise>
                    <p><xsl:apply-templates select="text()"/></p>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:when>
        <xsl:when test="html:a">
            <p>
                <xsl:apply-templates/>
            </p>
        </xsl:when>
        <xsl:otherwise>
            <xsl:apply-templates/>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="html:span">
    <xsl:apply-templates/><xsl:text> </xsl:text>
</xsl:template>

<xsl:template match="html:div/html:span|html:td/html:span">
    <p>
        <xsl:apply-templates/>
    </p>
</xsl:template>

<!-- other formatting -->
<xsl:template match="html:note">
    <xsl:choose>
        <xsl:when test="text()">
            <xsl:choose>
                <xsl:when test="ancestor::html:p|ancestor::html:b|ancestor::html:i|ancestor::html:u|ancestor::html:a|ancestor::html:dt|ancestor::html:h1|ancestor::html:h2|ancestor::html:h3|ancestor::html:h4|ancestor::html:strong|ancestor::html:span|ancestor::html:li">
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

<xsl:template match="html:font">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="html:ol/html:i">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="html:div/html:font|html:td/html:font">
    <p>
        <xsl:apply-templates/>
    </p>
</xsl:template>

<xsl:template match="pb">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="html:title">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="html:nobr">
    <p>
        <xsl:apply-templates/>
    </p>
</xsl:template>

<xsl:template match="html:article">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="html:header">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="text()">
    <xsl:value-of select="normalize-space(.)"/><xsl:text> </xsl:text>
</xsl:template>

<xsl:template match="html:textarea">
    <p>
        <xsl:apply-templates />
    </p>
</xsl:template>

<xsl:template match="html:fieldset">
    <p>
        <xsl:apply-templates />
    </p>
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
<xsl:template match="html:br"/>
<xsl:template match="html:wbr"/>

</xsl:stylesheet>

