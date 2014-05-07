<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
				xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
				xmlns:svg="http://www.w3.org/2000/svg">

	<xsl:output method="xml"
		   version="1.0"
		   encoding="UTF-8"
		   indent="yes"
		   doctype-public="-//UIT//DTD Corpus V1.0//EN"
		   doctype-system="http://www.giellatekno.uit.no/dtd/corpus.dtd"/>

	<xsl:template match="/">
		<document>
			<body>
				<xsl:for-each select="//svg:text">
					<p>
						<xsl:value-of select="normalize-space(.)"/>
					</p>
				</xsl:for-each>
			</body>
		</document>
	</xsl:template>
</xsl:stylesheet>