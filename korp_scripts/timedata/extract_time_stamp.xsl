<?xml version="1.0"?>
<!--+
    |
    | change the 2004-xml-spreadsheet XML files into a simpler xml format
    | Usage: java net.sf.saxon.Transform -it main STYLESHEET_NAME.xsl inDir=INPUT_DIR
    +-->

<xsl:stylesheet version="2.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:xs="http://www.w3.org/2001/XMLSchema"
		exclude-result-prefixes="xsl xs">

  <xsl:strip-space elements="*"/>

  <xsl:output method="xml" name="xml"
              encoding="UTF-8"
              omit-xml-declaration="yes"
              indent="no"/>
  <xsl:output method="xml" name="html"
              encoding="UTF-8"
              omit-xml-declaration="yes"
              indent="yes"/>
  <xsl:output method="text" name="txt"
	      encoding="UTF-8"/>

  <xsl:param name="inDir" select="concat('vrt_', $cLang, '_', $date)"/>
  <xsl:param name="date" select="'20210520'"/>
  <xsl:param name="cDomain" select="'science'"/>
  <xsl:param name="cLang" select="'smj'"/>

  <xsl:variable name="cID" select="concat($cLang,'_',$cDomain,'_',$date)"/>
  <xsl:variable name="outDir" select="concat('timestamp_',$cLang,'_',$date)"/>
  <xsl:variable name="fileName" select="concat('metacheck_',$cLang,'_',$cDomain,'_',$date)"/>

  <xsl:variable name="oe" select="'txt'"/>
  <xsl:variable name="tb" select="'&#9;'"/>
  <xsl:variable name="nl" select="'&#xA;'"/>
  <xsl:variable name="debug" select="false()"/>
  <xsl:variable name="ws" select="'&#x20;&#xD;&#xA;&#x9;'"/>

  <xsl:template match="/" name="main">
    <xsl:message terminate="no">
      <xsl:value-of select="concat('Processing data from dir: ', $inDir)"/>
    </xsl:message>

    <!-- output -->
    <xsl:result-document href="{$outDir}/{$fileName}.txt" format="{$oe}">

      <xsl:for-each select="for $f in collection(concat($inDir, '?select=*.vrt;recurse=yes;on-error=warning')) return $f">

	<xsl:variable name="current_file" select="substring-before((tokenize(document-uri(.), '/'))[last()], '.vrt')"/>
	<xsl:variable name="current_dir" select="substring-before(document-uri(.), $current_file)"/>
	<xsl:variable name="current_location" select="concat($inDir, substring-after($current_dir, $inDir))"/>

	<xsl:call-template name="processFile">
	  <xsl:with-param name="file" select="."/>
	  <xsl:with-param name="name" select="$current_file"/>
	  <xsl:with-param name="ie" select="'vrt'"/>
	  <xsl:with-param name="relPath" select="$current_location"/>
	</xsl:call-template>
      </xsl:for-each>
    </xsl:result-document>

    </xsl:template>

  <!-- process file -->
  <xsl:template name="processFile">
    <xsl:param name="file"/>
    <xsl:param name="name"/>
    <xsl:param name="ie"/>
    <xsl:param name="relPath"/>

    <xsl:message terminate="no">
      <xsl:value-of select="concat('file: ', $relPath, $name, '.', $ie)"/>
    </xsl:message>

    <xsl:for-each select="$file//text">
      <xsl:value-of select="concat(./@datefrom, ' ', ./@dateto, ' ', ./@token_count, ' ', $nl)"/>
    </xsl:for-each>

    <xsl:if test="$debug">
      <xsl:message terminate="no">
	<xsl:value-of select="concat('   Done!',' Output file  ',$name,' in: ', $outDir)"/>
      </xsl:message>
    </xsl:if>

  </xsl:template>

</xsl:stylesheet>
