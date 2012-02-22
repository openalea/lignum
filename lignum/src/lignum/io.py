# TODO

# 1. Implement the full specification
# 2. Test all the cases with several examples
# 3. Implement a loop in OpenAlea
# 4. Use the PlantGL turtle

# 2.1. add a header
# 2.2. separate graph parsing and scenegraph generation
# 2.3. Error management
# 2.4. Documentation
# 2.5. Compute properties when it is possible (sphere, ...)
# 2.6. 2D draw of the graph

from StringIO import StringIO
from math import radians

import xml.etree.ElementTree as xml

#from openalea.core.graph.property_graph import PropertyGraph
from openalea.mtg import MTG, fat_mtg, turtle as mtg_turtle
import openalea.plantgl.all as pgl
Vector3 = pgl.Vector3


class Parser(object):

    def parse(self, fn):
        self.trash = []
        self._g = MTG()

        doc = xml.parse(fn)
        root = doc.getroot()

        self.dispatch(root)

        self._g = fat_mtg(self._g)

        return self._g

    def dispatch(self, elt):
        try:
            return self.__getattribute__(elt.tag)(elt.getchildren(), **elt.attrib)
        except Exception, e:
            print e
            raise Exception("Unvalid element %s"%elt.tag)
            


    def Tree(self, elts, **properties):
        """ A Tree with attributes, parameters and a recursive structure.

        Create a new tree (scale 1) in the MTG. Store TreeXX as properties of Tree vertex.

        :Parameters:
            - elts are TreeAttributes, TreeParameters, TreeFunctions and Axis which is recusive.
            - SegmentType
            - LeafType

        .. todo::
            SegmentType?
            LeafType: what are the possible values?

        """
        g = self._g

        # Add a new tree in the mtg
        self.tree_id = g.add_component(g.root, **properties)
        self.axes = []
        self.segments = []
        self.edges = ['<']

        g.node(self.tree_id).label = 'Tree'

        # Dispatch on Tree Attributes, TreeParameters and TreeFunctions.
        # Then Dispatch on Axis.

        for elt in elts:
            self.dispatch(elt)

        self.axes = []
        self.segments = []
        self.edges = []

    def TreeAttributes(self, elts):
        """ Add the attributes as a property of the MTG.

        """
        root = self._g.node(self.tree_id)
        root.point, root.direction, root.attributes = self._parse_attributes(elts)

    def TreeParameters(self, elts):
        root = self._g.node(self.tree_id)
        root.parameters = dict((a.tag, a.text) for a in elts)

    def TreeFunctions(self, elts):
        root = self._g.node(self.tree_id)
        root.functions= dict((a.tag, a.text) for a in elts)

    def Axis(self, elts):
        """ Create a new axis depending of the branching type
        """
        g = self._g
        edge_type = self.edges[-1]
        if not self.axes:
            self.axes.append(g.add_component(self.tree_id, label='Axis'))
        else:
            axis_id = self.axes[-1]
            new_axis = g.add_child(parent=axis_id, edge_type=edge_type, label='Axis')
            if edge_type == '+':
                self.axes.append(new_axis)
            else:
                self.axes[-1] = new_axis

        # Recursive structure
        for elt in elts:
            self.dispatch(elt)
        
        # end of the recursion
        
        if edge_type == '+':
            self.axes.pop()
            self.segments = self.segments[:len(self.axes)]
            self.edges[-1] = edge_type

    def AxisAttributes(self, elts):
        """ Add properties to the current Axis.
        """
        node = self._g.node(self.axes[-1])
        node.point, node.direction, node.attributes = self._parse_attributes(elts)

    def TreeSegment(self, elts, ObjectIndex=None):
        """ Add one internode at scale 3.
        """
        self.internode(elts, ObjectIndex=ObjectIndex, label='TreeSegment')

    def TreeSegmentAttributes(self, elts):
        """ Add properties to the current TreeSegment.
        """
        node = self._g.node(self.segments[-1])
        node.point, node.direction, node.attributes = self._parse_attributes(elts)

    def BranchingPoint(self, elts):
        """ Define a branching point. """
        g = self._g
        self.edges.append('+')

        for elt in elts:
            self.dispatch(elt)
        
        self.edges.pop()

    def BranchingPointAttributes(self, elts):
        """ Nothing to do because the BranchingPoint is not stored in the MTG.
        """
        pass

    def Bud(self, elts, ObjectIndex=None):
        """ Add a bud at the same scale at the end of an Axis. """
        self.internode(elts, ObjectIndex=ObjectIndex, label='Bud')

    BudAttributes = TreeSegmentAttributes

    def BroadLeaf(self, elts, **props):
        """ Add a BroadLeaf to a TreeSegment """
        g = self._g
        parent = self.segments[-1]
        leaf = g.add_child(parent, edge_type='+', 
                           label='BroadLeaf',**props)
        self.current_leaf = leaf
        for elt in elts:
            self.dispatch(elt)

    def BroadLeafAttributes(self, elts):
        node = self._g.node(self.current_leaf)
        node.attributes = dict((a.tag, a.text) for a in elts)

    def internode(self, elts, ObjectIndex=None, label='TreeSegment'):
        """ Shared method for TreeSegment and Bud.

        label is a TreeSegment or a Bud.
        """
        g = self._g
        edge_type = self.edges[-1]
        complex_axis = self.axes[-1]
        
        if not self.segments:
            self.segments.append(g.add_component(complex_axis, label=label, ObjectIndex=ObjectIndex))
        else:
            parent = self.segments[-1]
            # There is A BUG in add_child and complex with an existing complex!!!!
            
            if g.complex(parent) != complex_axis:
                new_segment = g.add_component(complex_axis)
                new_segment = g.add_child(parent, child=new_segment,
                                          edge_type=edge_type, label=label,
                                          ObjectIndex=ObjectIndex)
            else:
                new_segment = g.add_child(parent, 
                                          edge_type=edge_type, label=label,
                                          ObjectIndex=ObjectIndex)

            if edge_type == '+':
                self.segments.append(new_segment)
            else: 
                self.segments[-1] = new_segment

        # Property management
        for elt in elts:
            self.dispatch(elt)
        
        # The first segment is '+'. Others are < until the next branching point.
        if edge_type == '+':
            self.edges[-1] = '<'

    @staticmethod
    def _parse_attributes(elts) :
        d = dict((a.tag, a.text) for a in elts)
        point = d.pop('point')
        direction = d.pop('direction')
        return point, direction, d 


##########################################################################

class Dumper(object):

    def dump(self, graph):
        self._graph = graph
        self.graph()
        return xml.tostring(self.doc)

    def SubElement(self, *args, **kwds):
        elt = xml.SubElement(*args, **kwds)
        if not elt.text:
            elt.text = '\n\t'
        elt.tail = '\n\t'
        return elt

    def graph(self):
        self.doc = xml.Element('graph')
        self.doc.tail = '\n'
        self.doc.text = '\n\t'
        # add root
        root = self._graph.root
        self.SubElement(self.doc, 'root', dict(root_id=str(root)))
        # universal types
        self.universal_node()

        for vid in self._graph.vertices():
            self.node(vid)

        for eid in self._graph.edges():
            self.edge(eid)

        
    def universal_node(self):
        # test
        _types = self._graph._types
        #_types['Boid']=['sphere']
        attrib = {}
        if _types:
            for t, extends in _types.iteritems():
                attrib['name'] = t
                user_type = self.SubElement(self.doc, 'type', attrib)
                for t in extends:
                    attrib['name'] = t
                    self.SubElement(user_type, 'extends', attrib)

    def node(self, vid):
        g = self._graph

        pname = g.vertex_property('name')
        ptype = g.vertex_property('type')
        properties = g.vertex_property('parameters')

        if vid == g.root and vid not in pname:
            # The root node has been only declared
            # by <root root_id="1"/>
            return

        attrib = {}
        attrib['id'] = str(vid)
        attrib['name'] = pname[vid]
        attrib['type'] = ptype[vid]
        node = self.SubElement(self.doc, 'node', attrib)
        if not g.vertex_property('geometry').get(vid):
            t = g.vertex_property('transform').get(vid)
            if t:
                transfo = self.SubElement(node, 
                    'property', 
                    {'name':'transform'})
                matrix = self.SubElement(transfo, 'matrix')
                s='\n'
                for i in range(4):
                    c = tuple(t.getRow(i))
                    s += '\t\t\t%.5f %.5f %.5f %.5f\n'%c
                matrix.text = s+'\n' 

        for (name, value) in properties.get(vid,[]).iteritems():
            attrib = {'name':name, 'value':str(value)}
            self.SubElement(node, 'property', attrib)
        
    def edge(self, eid):
        edge_type_conv = {}
        edge_type_conv['<'] = 'successor'
        edge_type_conv['+'] = 'branch'
        g = self._graph
        edge_type = g.edge_property('edge_type').get(eid)
        attrib = {}
        attrib['id'] = str(eid)
        attrib['src_id'] = str(g.source(eid))
        attrib['dest_id'] = str(g.target(eid))
        if edge_type:
            attrib['type'] = edge_type_conv[edge_type]

        self.SubElement(self.doc, 'edge', attrib)

##########################################################################
# Turtle function to represent a LIGNUM MTG

def lignum_turtle(g):
    """ Plot in 3D an MTG generated from LIGNUM XML Tree using a turtle.

    """

    COLOR_SEGMENT = 1
    COLOR_LEAF = 2
    COLOR_BUD= 3
    PETIOL_RADIUS = 0.001
    BUD_SIZE = 0.01
    BUD_GEOM = pgl.Translated((0,0,BUD_SIZE),
                              pgl.Scaled((1/3.,1/3.,1), pgl.Sphere(radius=BUD_SIZE)))

    # Define the global properties first:
    # Base diameter LGADbase
    n = g.node(1)
    position = Vector3(map(float,n.point.split()))
    param = pgl.TurtleParam()
    param.position = position
    myTurtle = pgl.PglTurtle(param)
    
    def lignum_visitor(g, v, turtle):
        n = g.node(v)
        turtle.setId(v)

        param = turtle.getParameters()

        def my_leaf(xs, ys):
            return pgl.Translated((xs/2,0,0),
                              pgl.Scaled((1,ys/xs,1), pgl.Disc(radius=xs/2)))
        def setDir(d):
            up = (d^turtle.getUp())^d
            turtle.setHead(direction, up)

        if n.label == 'TreeSegment':
            turtle.setColor(COLOR_SEGMENT)
            radius = float(n.attributes['LGAR'])
            length = float(n.attributes['LGAL'])
            position = Vector3(map(float,n.point.split()))
            direction = Vector3(map(float,n.direction.split()))

            turtle.move(position)
            turtle.setWidth(radius)
            setDir(direction)
            turtle.F(length)
        elif n.label == 'Bud':
            turtle.setColor(COLOR_BUD)
            position = Vector3(map(float,n.point.split()))
            direction = Vector3(map(float,n.direction.split()))
            turtle.move(position)
            setDir(direction)
            turtle.customGeometry(BUD_GEOM)
        elif n.label == 'BroadLeaf':
            petiol_start = Vector3(map(float,n.attributes['PetioleStart'].split()))
            petiol_end = Vector3(map(float,n.attributes['PetioleEnd'].split()))
            leaf_normal = Vector3(map(float,n.attributes['LeafNormal'].split()))
            xdir = Vector3(map(float,n.attributes['xdir'].split()))
            ydir = Vector3(map(float,n.attributes['ydir'].split()))
            xsize = float(n.attributes['EllipseSMajorA'])
            ysize = float(n.attributes['EllipseSMinorA'])

            # petiol
            turtle.setColor(COLOR_SEGMENT)
            turtle.move(petiol_start)
            turtle.setWidth(PETIOL_RADIUS)
            turtle.lineTo(petiol_end)

            # leaf
            turtle.setColor(COLOR_LEAF)
            turtle.setHead(leaf_normal,xdir)
            turtle.customGeometry(my_leaf(xsize,ysize))


    scene = mtg_turtle.TurtleFrame(g,lignum_visitor,myTurtle)
    return scene


##########################################################################
# Wrapper functions for OpenAlea usage.

def xml2mtg(xml_graph):
    """
    Convert a xml string to a MTG.
    """
    #f = StringIO(xml_graph)
    f = xml_graph
    parser = Parser()
    g = parser.parse(f)
    #f.close()
    return g
    

def mtg2xml(graph):
    dump = Dumper()
    return dump.dump(graph)

