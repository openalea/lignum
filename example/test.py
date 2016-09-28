import lignum
from lignum.io import xml2mtg, mtg2xml, lignum_turtle
from openalea.mtg import *
from openalea.plantgl.all import Viewer, Scene

from openalea.deploy import shared_data


file_names = shared_data.shared_data(lignum,share_path="../../share/stump2", pattern='Growth*.xml')
#print file_names

#for fn in file_names:
#    if '62' in fn:
#        break

#file_names = [fn]

#fn = file_names[0]
#g = xml2mtg(fn)
#scene = lignum_turtle(g)

# Calcul du MTG

gs = []
scenes = []
for fn in file_names:
    g = xml2mtg(fn)
    gs.append(g)

# Compute Color
lut = {}
lut[0] = (255, 110,50)
lut[1] = (0,255,0)
lut[2] = (0,0,255)
for g in gs:
    ct = g.property('LGAtype')
    _colors = dict((v, lut.get(int(x),(0,127,127))) for v, x in ct.iteritems())
    g.properties()['color'] = _colors
    labels = g.property('label')
    for v, label in labels.iteritems():
        if label == 'Bud':
            _colors[v] = _colors[g.parent(v)]

# Compute scenes
scenes = []
i= 0
for g in gs:
    scene = lignum_turtle(g, has_color=True)
    scenes.append(scene)

# Merge scenes

scene = Scene()
for sc in scenes:
    scene.merge(sc)

