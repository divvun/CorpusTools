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

  <!--xsl:strip-space elements="*"/-->

  <xsl:output method="xml" name="vrt"
              encoding="UTF-8"
              omit-xml-declaration="yes"
              indent="no"/>
  <xsl:output method="text" name="txt"
	      encoding="UTF-8"/>

  <!-- in -->
  <xsl:param name="cDomain" select="'ficti'"/>
  <xsl:param name="cLang" select="'sme'"/>
  <xsl:param name="inDir" select="concat('_od_', $cLang, '._.', $cDomain)"/>
  <xsl:param name="date" select="'20210625'"/>

  <xsl:variable name="cID" select="concat($cLang,'_',$cDomain,'_',$date)"/>
  <xsl:variable name="outDir" select="concat('vrt_',$cLang,'_',$date)"/>
  <xsl:variable name="outFile" select="$cID"/>

  <xsl:variable name="oe" select="'vrt'"/>
  <xsl:variable name="tb" select="'&#9;'"/>
  <xsl:variable name="nl" select="'&#xA;'"/>
  <xsl:variable name="debug" select="false()"/>
  <xsl:variable name="ws" select="'&#x20;&#xD;&#xA;&#x9;'"/>

  <xsl:template match="/" name="main">

    <xsl:message terminate="no">
      <xsl:value-of select="concat('Processing data from dir: ', $inDir)"/>
    </xsl:message>

	<!--xsl:for-each select=""-->

    <xsl:result-document href="{$outDir}/{$outFile}.{$oe}" format="{$oe}">
      <corpus id="{$cID}">
        <xsl:value-of select="$nl"/>
	<xsl:for-each select="for $f in (collection(concat($inDir, '?select=*.xml;recurse=yes;on-error=warning'))) return $f">

	  <xsl:variable name="current_file" select="substring-before((tokenize(document-uri(.), '/'))[last()], '.xml')"/>
	  <xsl:variable name="current_dir" select="substring-before(document-uri(.), $current_file)"/>
	  <xsl:variable name="current_location" select="concat($inDir, substring-after($current_dir, $inDir))"/>

	  <xsl:message terminate="no">
	    <xsl:value-of select="concat('file: ', $current_location, $current_file, '.xml')"/>
	  </xsl:message>

	  <xsl:variable name="text_ID" select="concat($cDomain, '_t', position())"/>

	  <!-- natural order of text attributes -->

	  <text
	      id="{$text_ID}"
	      title="{./text/@title}"
	      lang="{./text/@lang}"
	      orig_lang="{./text/@orig_lang}"
	      gt_domain="{./text/@gt_domain}"
	      first_name="{./text/@first_name}"
	      last_name="{./text/@last_name}"
	      nationality="{./text/@nationality}"
	      date="{./text/@date}"
	      datefrom="{./text/@datefrom}"
	      dateto="{./text/@dateto}"
	      timefrom="{./text/@timefrom}"
	      timeto="{./text/@timeto}"
	      >
	    <xsl:attribute name="sentence_count">

	      <xsl:variable name="tmp">
		<xsl:for-each select="./text/sentence">
		  <xsl:value-of select="count(tokenize(./text(), $nl))-2"/>
		  <xsl:if test="not(position()=last())">
		    <xsl:value-of select="'_'"/>
		  </xsl:if>
		</xsl:for-each>
	      </xsl:variable>

	      <xsl:value-of select="count(tokenize($tmp,'_'))"/>

	    </xsl:attribute>

	    <xsl:attribute name="token_count">

	      <xsl:variable name="tmp">
		<xsl:for-each select="./text/sentence">
		  <xsl:value-of select="count(tokenize(./text(), $nl))-2"/>
		  <xsl:if test="not(position()=last())">
		    <xsl:value-of select="'_'"/>
		  </xsl:if>
		</xsl:for-each>
	      </xsl:variable>


	      <xsl:value-of select="sum(for $i in tokenize($tmp,'_')[.] return number($i))"/>

	    </xsl:attribute>


	    <xsl:value-of select="$nl"/>
	    <xsl:for-each select="./text/sentence">
	      <sentence id="{concat($text_ID, '_s', position())}">
		<xsl:attribute name="token_count">
		  <xsl:value-of select="count(tokenize(./text(), $nl))-2"/>
		</xsl:attribute>
		<xsl:value-of select="replace(., ' ', '_')"/>
	      </sentence>
	      <xsl:value-of select="$nl"/>
	    </xsl:for-each>
	  </text>
	  <xsl:value-of select="$nl"/>
	</xsl:for-each>
      </corpus>
      <xsl:value-of select="$nl"/>
    </xsl:result-document>
  <!--/xsl:for-each-->

  </xsl:template>

</xsl:stylesheet>
