#X from openalea.mtg import MTG
#X import xml.etree.ElementTree as xml
#X 
#X fn = r'C-SugarMaple.xml'
#X doc = xml.parse(fn)
#X root = doc.getroot()

from lignum.io import *

def test1():
    fn = r'C-pine.xml'
    g = xml2mtg(fn)
    scene = lignum_turtle(g)

    assert len(g) == 38
    assert g.nb_scales() == 4
    assert g.nb_vertices(scale=1) == 1
    assert g.nb_vertices(scale=2) == 15
    assert g.nb_vertices(scale=3) == 21

    assert len(scene) == 20
    
def test2():
    fn = r'C-SugarMaple.xml'
    g = xml2mtg(fn)
    scene = lignum_turtle(g)

    assert len(g) == 149
    assert g.nb_scales() == 4
    assert g.nb_vertices(scale=1) == 1
    assert g.nb_vertices(scale=2) == 47
    assert g.nb_vertices(scale=3) == 100

    assert len(scene) == 118

def test3():
    fn = r'this9-1-2-10.xml'
    g = xml2mtg(fn)
    scene = lignum_turtle(g)

    assert len(g) == 1427
    assert g.nb_scales() == 4
    assert g.nb_vertices(scale=1) == 1
    assert g.nb_vertices(scale=2) == 460
    assert g.nb_vertices(scale=3) == 965

    assert len(scene) == 827

# Interactive test
"""
fn = r'this9-1-2-10.xml'
g = xml2mtg(fn)
scene = lignum_turtle(g)

mtg_turtle.Plot(scene)

"""
