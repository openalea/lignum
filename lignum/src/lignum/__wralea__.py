
# This file has been generated at Wed Mar 14 12:20:51 2012

from openalea.core import *


__name__ = 'lignum'

__editable__ = True
__description__ = 'OpenAlea / Lignum.'
__license__ = 'CECILL-C'
__url__ = 'http://openalea.gforge.inria.fr'
__alias__ = []
__version__ = '0.0.1'
__authors__ = 'C. Pradal, Risto Sievanen'
__institutes__ = 'INRIA/CIRAD/Metla'
__icon__ = ''


__all__ = ['io_lignum_turtle', 'io_xml2mtg', '_179421648']



io_lignum_turtle = Factory(name='turtle',
                authors='C. Pradal, Risto Sievanen (wralea authors)',
                description='',
                category='geometry',
                nodemodule='io',
                nodeclass='lignum_turtle',
                inputs=({'name': 'mtg', 'desc': 'MTG'},),
                outputs=({'name': 'scene', 'desc': '3D scene'},),
                widgetmodule=None,
                widgetclass=None,
               )




io_xml2mtg = Factory(name='xml2mtg',
                authors='C. Pradal, Risto Sievanen (wralea authors)',
                description='',
                category='io',
                nodemodule='io',
                nodeclass='xml2mtg',
                inputs=({'interface': IFileStr, 'name': 'xml_graph', 'value': '', 'desc': 'Lignum Graph description in xml with 3D information.'},),
                outputs=({'name': 'MTG', 'desc': 'MTG.'},),
                widgetmodule=None,
                widgetclass=None,
               )




_179421648 = CompositeNodeFactory(name='tutorial MTG',
                             description='',
                             category='Unclassified',
                             doc='',
                             inputs=[],
                             outputs=[],
                             elt_factory={  2: ('lignum', 'xml2mtg'),
   3: ('lignum', 'turtle'),
   4: ('vplants.plantgl.visualization', 'plot3D')},
                             elt_connections={  16414792: (3, 0, 4, 0), 16414816: (2, 0, 3, 0)},
                             elt_data={  2: {  'block': False,
         'caption': 'xml2mtg',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0x93dc150> : "xml2mtg"',
         'hide': True,
         'id': 2,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 4.5017671592412185,
         'posy': 8.86908077994429,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   3: {  'block': False,
         'caption': 'turtle',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0x972f9d0> : "turtle"',
         'hide': True,
         'id': 3,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 16.556174288604616,
         'posy': 45.39596175907715,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   4: {  'block': False,
         'caption': 'plot3D',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0x8b5add0> : "plot3D"',
         'hide': True,
         'id': 4,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 15.264357587598191,
         'posy': 82.24680130468099,
         'priority': 0,
         'use_user_color': False,
         'user_application': True,
         'user_color': None},
   '__in__': {  'block': False,
                'caption': 'In',
                'delay': 0,
                'hide': True,
                'id': 0,
                'lazy': True,
                'port_hide_changed': set(),
                'posx': 0,
                'posy': 0,
                'priority': 0,
                'use_user_color': True,
                'user_application': None,
                'user_color': None},
   '__out__': {  'block': False,
                 'caption': 'Out',
                 'delay': 0,
                 'hide': True,
                 'id': 1,
                 'lazy': True,
                 'port_hide_changed': set(),
                 'posx': 0,
                 'posy': 0,
                 'priority': 0,
                 'use_user_color': True,
                 'user_application': None,
                 'user_color': None}},
                             elt_value={  2: [(0, "'/home/pradal/devlp/aleapkg/lignum/test/test.xml'")],
   3: [],
   4: [],
   '__in__': [],
   '__out__': []},
                             elt_ad_hoc={  2: {'position': [4.5017671592412185, 8.86908077994429], 'userColor': None, 'useUserColor': False},
   3: {'position': [16.556174288604616, 45.39596175907715], 'userColor': None, 'useUserColor': False},
   4: {'position': [15.264357587598191, 82.24680130468099], 'userColor': None, 'useUserColor': False},
   '__in__': {'position': [0, 0], 'userColor': None, 'useUserColor': True},
   '__out__': {'position': [0, 0], 'userColor': None, 'useUserColor': True}},
                             lazy=True,
                             eval_algo='LambdaEvaluation',
                             )




