#!/usr/bin/python
# # -*- coding: utf-8 -*-

"""
**COMPLETION** = 1%  Sphinx Approved = *False*

.. topic:: Overview

    This module handles the xml format for data.

    :Date: 3/16/2015
    :Author: **Craig Gunter**

"""

import xml.etree.ElementTree as ET

root = ET.Element("root")

doc = ET.SubElement(root, "doc")

field1 = ET.SubElement(doc, "field1")
field1.set("name", "blah")
field1.text = "some value1"

field2 = ET.SubElement(doc, "field2")
field2.set("name", "asdfasd")
field2.text = "some vlaue2"

tree = ET.ElementTree(root)
tree.write("filename.xml")

captionTree=ET.parse('Graphics/LX1750-CapStripe.svg')
svg=captionTree.getroot()

color='#000000'
namespace='{http://www.w3.org/2000/svg}'

for groupLevel_1 in svg:
	print groupLevel_1.tag, groupLevel_1.attrib['id']
	if groupLevel_1.attrib['id']=='Captions':
		for childLevel_1 in groupLevel_1:
			if childLevel_1.tag==namespace+'path':
				childLevel_1.set('fill',color)
			elif childLevel_1.tag==namespace+'g':
				for groupLevel_2 in childLevel_1:
					if groupLevel_2.tag==namespace+'path':
						groupLevel_2.set('fill',color)
					elif groupLevel_2.tag==namespace+'g':
						for groupLevel_3 in groupLevel_2:
							if groupLevel_3.tag==namespace+'path':
								groupLevel_3.set('fill',color)

captionTree.write('Graphics/LX1750.svg', encoding='utf-8', xml_declaration=True)
