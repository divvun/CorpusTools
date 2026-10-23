<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:html="http://www.w3.org/1999/xhtml"
                xmlns:saxon="http://icl.com/saxon"
                xmlns:udhr="http://www.unhchr.ch/udhr"
                exclude-result-prefixes="xsl fo html saxon udhr">
<!--$Revision: 38657 $ -->

<!--
Usage:
xsltproc xhtml2corpus.xsl <tmx-file> > file.html
-->

<xsl:strip-space elements="*"/>

<xsl:output method="xml"
		   version="1.0"
		   encoding="UTF-8"
		   indent="yes"/>

<!-- Main block-level conversions -->
    <xsl:template match="udhr:udhr">
        <html>
            <head>
                <meta charset="UTF-8"/>
            </head>
            <body>
                <xsl:apply-templates/>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="udhr:udhr/udhr:title">
        <h1><xsl:apply-templates select="@*|node()" /></h1>
    </xsl:template>

    <xsl:template match="udhr:preamble">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="udhr:preamble/udhr:title"/>

    <xsl:template match="udhr:article/udhr:title">
        <h2><xsl:apply-templates/></h2>
    </xsl:template>

    <xsl:template match="udhr:article">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="udhr:para">
        <p><xsl:apply-templates select="@*|node()" /></p>
    </xsl:template>

    <xsl:template match="udhr:orderedlist">
        <ol>
            <xsl:apply-templates select="@*|node()" />
        </ol>
    </xsl:template>

    <xsl:template match="udhr:listitem">
        <li><xsl:apply-templates/></li>
    </xsl:template>

</xsl:stylesheet>
