#X from openalea.mtg import MTG
#X import xml.etree.ElementTree as xml
#X 
#X fn = r'C-SugarMaple.xml'
#X doc = xml.parse(fn)
#X root = doc.getroot()

from lignum.io import *

fn = r'C-pine.xml'
g = xml2mtg(fn)
sc1 = lignum_turtle(g)

fn = r'C-SugarMaple.xml'
g2 = xml2mtg(fn)
sc2 = lignum_turtle(g2)

fn = r'this9-1-2-10.xml'
g = xml2mtg(fn)
sc1 = lignum_turtle(g)

mtg_turtle.Plot(sc1)
