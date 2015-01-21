<?xml version="1.0" encoding="UTF-8"?>
<!--+
    | Preprocess the file-specific xsl stylesheet to import the common
    | xsl stylesheet from $GTHOME instead of
    | /usr/local/share/corp/bin/common.xsl (the default).
    +-->

<x:stylesheet
    xmlns:x="http://www.w3.org/1999/XSL/Transform"
    xmlns:xsl="anything"
    version="1.0">

    <x:output method="xml"
              version="1.0"
              encoding="UTF-8"/>

    <x:namespace-alias stylesheet-prefix="xsl" result-prefix="x"/>

    <x:param name="commonxsl" select="'/usr/local/share/corp/bin/common.xsl'"/>

    <!-- Remove existing xsl:import and xsl:output elements: -->
    <x:template match="//*[local-name()='import']"/>
    <x:template match="//*[local-name()='output']"/>

    <!-- Construct a new root element with the proper import ref: -->
    <x:template match="/*[local-name()='stylesheet']">
        <xsl:stylesheet version="1.0">
            <x:text>

            </x:text>
            <xsl:import href="{$commonxsl}"/>
            <x:text>

            </x:text>
            <xsl:output method="xml"
                        version="1.0"
                        encoding="UTF-8"
                        indent="yes"
                        doctype-public="-//UIT//DTD Corpus V1.0//EN"
                        doctype-system="http://giellatekno.uit.no/dtd/corpus.dtd"/>
            <x:apply-templates/>
        </xsl:stylesheet>

    </x:template>

    <!-- Copy everything else -->
    <x:template match="node()|@*">
        <x:copy>
            <x:apply-templates select="node()|@*" />
        </x:copy>
    </x:template>

</x:stylesheet>
