<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                xmlns:html="http://www.w3.org/1999/xhtml"
                xmlns:saxon="http://icl.com/saxon"
                exclude-result-prefixes="xsl fo html saxon">
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
<xsl:template match="body">
	<html>
        <head>
            <meta charset="UTF-8"/>
        </head>
        <body>
            <table border="2">
                <xsl:apply-templates/>
            </table>
        </body>
	</html>
</xsl:template>

<xsl:template match="tu">
    <tr>
        <xsl:apply-templates/>
    </tr>
</xsl:template>

<xsl:template match="tuv">
    <td>
        <xsl:value-of select="seg"/>
    </td>
</xsl:template>

</xsl:stylesheet>
