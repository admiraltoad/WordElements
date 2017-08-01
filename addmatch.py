"""
    Word Elements :: addmatch
    
"""
import os, sys
import pyapp
import xml.dom.minidom
from xml.etree import ElementTree as etree





if __name__ == "__main__":  
    
    args = pyapp.get_system_arguments()

    if len(args) != 2:
        raise Exception("Invalid entry!")

    master = args[0]
    slave = args[1]

    root = etree.Element("root")
    doc = etree.SubElement(root, "match")

    etree.SubElement(doc, "master").text = master
    etree.SubElement(doc, "slave").text = slave

    tree = etree.ElementTree(root)
    tree.write("temp.xml")

    xml = xml.dom.minidom.parse("temp.xml") # or xml.dom.minidom.parseString(xml_string)
    pretty_xml_as_string = xml.toprettyxml()

    f = open("dictionary.xml", "w")
    f.write(pretty_xml_as_string)
    f.close()

    sys.exit(0)
