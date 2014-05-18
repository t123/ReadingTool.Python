<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  	<xsl:output method="text" indent="no" omit-xml-declaration="yes" />
    <xsl:template match="/">
        <xsl:text>\documentclass[fontsize=9pt]{scrartcl}
\usepackage[utf8]{inputenc}
\usepackage[paperwidth=9cm, paperheight=12cm, top=1cm, left=1cm, right=1cm, bottom=1cm]{geometry}
\usepackage{graphicx}
\usepackage{perpage}
\usepackage[T1]{fontenc}
\usepackage[scaled]{helvet}
\renewcommand*\familydefault{\sfdefault} 
\frenchspacing
\sloppy
\pagestyle{empty}
\usepackage[pdftex,
    pdfauthor={</xsl:text><xsl:value-of select="//root/content/@author"/><xsl:text>},
    pdftitle={</xsl:text><xsl:value-of select="//root/content/@title"/><xsl:text>},
    pdfcreator={ReadingTool}]{hyperref}
\sloppy
\pagestyle{empty}
\MakePerPage[1]{footnote}
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
    	<xsl:text>/*</xsl:text>
        <xsl:apply-templates select="sentence"/>
        <xsl:text>*/

</xsl:text>
    </xsl:template>
    <xsl:template match="sentence">
    	<xsl:apply-templates />
    </xsl:template>
    <xsl:template match="fragment">
   		<xsl:apply-templates />
   		<xsl:if test="string-length(@definition)>0 and @state='unknown'">
      		<xsl:text> \footnote{</xsl:text>
            	<xsl:value-of select="@definition" />
            <xsl:text>}</xsl:text>
      	</xsl:if>
    </xsl:template>
    <xsl:template match="term">
      	<xsl:value-of select="."/>
      	<xsl:if test="string-length(@definition)>0 and @state='unknown'">
      		<xsl:text> \footnote{</xsl:text>
            	<xsl:value-of select="@definition" />
            <xsl:text>}</xsl:text>
      	</xsl:if>
    </xsl:template>
    <xsl:template match="whitespace">
  	<xsl:value-of select="."/>
  </xsl:template>
  <xsl:template match="number">
  	<xsl:value-of select="."/>
  </xsl:template>
  <xsl:template match="punctuation">
  	<xsl:value-of select="."/>
  </xsl:template>
  <xsl:template match="tag"></xsl:template>
</xsl:stylesheet>