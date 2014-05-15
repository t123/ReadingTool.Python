<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  	<xsl:output method="text" indent="no" omit-xml-declaration="yes" />
    <xsl:template match="/">
        <xsl:text>\documentclass[8pt]{article}
\usepackage[papersize={90mm,120mm},margin=2mm]{geometry}
\usepackage[kerning=true]{microtype}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[charter]{mathdesign}
\usepackage[normalmargins]{savetrees}
\usepackage[pdftex,
    pdfauthor={</xsl:text><xsl:value-of select="//root/content/@author"/><xsl:text>},
    pdftitle={</xsl:text><xsl:value-of select="//root/content/@title"/><xsl:text>},
    pdfcreator={ReadingTool}]{hyperref}
\sloppy
\pagestyle{empty}
\begin{document}
</xsl:text>
<xsl:apply-templates select="//root/content/join" />
<xsl:text>\end{document}
</xsl:text>
    </xsl:template>
    <xsl:template match="join">
    	<xsl:apply-templates select="paragraph" />
    </xsl:template>
    <xsl:template match="paragraph">
    	<xsl:text>\paragraph{</xsl:text>
        <xsl:apply-templates select="sentence"/>
        <xsl:text>}

        </xsl:text>
    </xsl:template>
    <xsl:template match="sentence">
    	<xsl:apply-templates />
    </xsl:template>
    <xsl:template match="fragment">
   		<xsl:apply-templates select="term"/>
   		<xsl:if test="string-length(@definition)>0 and @state='unknown'">
      		<xsl:text> \protect\footnote{</xsl:text>
            	<xsl:value-of select="@definition" />
            <xsl:text>}</xsl:text>
      	</xsl:if>
    </xsl:template>
    <xsl:template match="term">
    	<xsl:choose> 
      <xsl:when test="@isTerm='True'">
      	<xsl:value-of select="."/>
      	<xsl:if test="string-length(@definition)>0 and @state='unknown'">
      		<xsl:text> \protect\footnote{</xsl:text>
            	<xsl:value-of select="@definition" />
            <xsl:text>}</xsl:text>
      	</xsl:if>
      </xsl:when>
      <xsl:otherwise>
          <xsl:value-of select="."/>
      </xsl:otherwise>
    </xsl:choose>
    </xsl:template>
</xsl:stylesheet>