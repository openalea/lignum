# Test convert Lignum XML to MTG and 3D representation
from lignum.io import *
from StringIO import StringIO

def test1():
    fn = r'C-pine.xml'
    g = xml2mtg(fn)
    s = mtg2xml(g)
    
    f = StringIO(s)
    g_bis = xml2mtg(f)
    f.close()

    assert len(g) == len(g_bis)
    for v in g:
        assert g.parent(v) == g_bis.parent(v)
        assert g.complex(v) == g_bis.complex(v)
    

# Interactive test
"""
from lignum import io
fn = r'this9-1-2-10.xml'
fn = r'C-pine.xml'
g = io.xml2mtg(fn)
s = io.mtg2xml(g)

fn = 'test.xml'
f = open(fn,'w')
f.write(s)
f.close()
g_bis = io.xml2mtg(fn)
scene = io.lignum_turtle(g_bis)
io.mtg_turtle.Plot(scene)
"""
