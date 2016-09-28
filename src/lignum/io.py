##############################################################################
# XML Lignum reader and writer.
##############################################################################

# from StringIO import StringIO
# from math import radians

# from os import path

import xml.etree.ElementTree as xml
from tempfile import mkstemp

# from openalea.core.graph.property_graph import PropertyGraph
from openalea.mtg import MTG, fat_mtg, turtle as mtg_turtle
from openalea.mtg import traversal
from openalea.mtg.plantframe import color as mtg_color

import openalea.plantgl.all as pgl
Vector3 = pgl.Vector3


class Parser(object):
    """ Read an XML file an convert it into an MTG.

    """

    def parse(self, fn):
        self.trash = []
        self._g = MTG()

        # Current proxy node for managing properties
        self._node = None

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
            raise Exception("Unvalid element %s" % elt.tag)

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

        self._node = g.node(self.tree_id)
        self._node.label = 'Tree'

        # Dispatch on Tree Attributes, TreeParameters and TreeFunctions.
        # Then Dispatch on Axis.

        for elt in elts:
            self.dispatch(elt)

        self.axes = []
        self.segments = []
        self.edges = []

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

        self._node = g.node(self.axes[-1])

        # Recursive structure
        for elt in elts:
            self.dispatch(elt)

        # end of the recursion

        if edge_type == '+':
            self.axes.pop()
            self.segments = self.segments[:len(self.axes)]
            self.edges[-1] = edge_type

    def TreeSegment(self, elts, **props):
        """ Add one internode at scale 3.
        """
        self.internode(elts, label='TreeSegment', **props)

    def BranchingPoint(self, elts):
        """ Define a branching point. """
        self.edges.append('+')

        for elt in elts:
            self.dispatch(elt)

        self.edges.pop()

    def BranchingPointAttributes(self, elts):
        """ Nothing to do because the BranchingPoint is not stored in the MTG.
        """
        pass

    def Bud(self, elts, **props):
        """ Add a bud at the same scale at the end of an Axis. """
        self.internode(elts, label='Bud', **props)

    def BroadLeaf(self, elts, **props):
        """ Add a BroadLeaf to a TreeSegment """
        g = self._g
        parent = self.segments[-1]
        leaf = g.add_child(parent, edge_type='+',
                           label='BroadLeaf', **props)
        self._node = g.node(leaf)
        for elt in elts:
            self.dispatch(elt)

    def internode(self, elts, label='TreeSegment', **props):
        """ Shared method for TreeSegment and Bud.

        label is a TreeSegment or a Bud.
        """
        g = self._g
        edge_type = self.edges[-1]
        complex_axis = self.axes[-1]

        if not self.segments:
            new_segment = g.add_component(complex_axis, label=label, **props)
            self.segments.append(new_segment)
        else:
            parent = self.segments[-1]
            # There is A BUG in add_child and complex with an existing complex!!!!

            if g.complex(parent) != complex_axis:
                new_segment = g.add_component(complex_axis)
                new_segment = g.add_child(parent, child=new_segment,
                                          edge_type=edge_type, label=label,
                                          **props)
            else:
                new_segment = g.add_child(parent,
                                          edge_type=edge_type, label=label,
                                          **props)

            if edge_type == '+':
                self.segments.append(new_segment)
            else:
                self.segments[-1] = new_segment

        self._node = g.node(self.segments[-1])

        # Property management
        for elt in elts:
            self.dispatch(elt)

        # The first segment is '+'. Others are < until the next branching point.
        if edge_type == '+':
            self.edges[-1] = '<'

    def update_attributes(self, elts):
        """ Update the properties in the MTG """
        proxy_node = self._node
        for a in elts:
            proxy_node.__setattr__(a.tag, a.text)

    TreeParameters = TreeFunctions = TreeAttributes = update_attributes
    AxisAttributes = update_attributes
    TreeSegmentAttributes = update_attributes
    BroadLeafAttributes = BudAttributes = TreeSegmentAttributes


##########################################################################

class Dumper(object):
    """ Convert an MTG into the LIGNUM XML format

    """

    def dump(self, graph):
        self._g = graph
        self.mtg()

        return '\n'.join(xml.tostring(tree) for tree in self.trees)

    def SubElement(self, *args, **kwds):
        elt = xml.SubElement(*args, **kwds)
        if not elt.text:
            elt.text = '\n'
        elt.tail = '\n'
        return elt

    def mtg(self):
        """ Convert the MTG into a XML tree. """
        g = self._g
        # Create a DocType at the begining of the file

        # Traverse the MTG
        self.trees = []
        self.xml_nodes = {}
        self.branching_point = {}
        # self.spaces = 0
        for tree_id in g.components_iter(g.root):
            self.Tree(tree_id)

            for vid in traversal.iter_mtg2(g, tree_id):
                if vid == tree_id:
                    continue

                self.process_vertex(vid)
# X         self.doc = xml.Element('graph')
# X         self.doc.tail = '\n'
# X         self.doc.text = '\n\t'
# X         # add root
# X         root = self._graph.root
# X         self.SubElement(self.doc, 'root', dict(root_id=str(root)))
# X         # universal types
# X         self.universal_node()
# X
# X         for vid in self._graph.vertices():
# X             self.node(vid)
# X
# X         for eid in self._graph.edges():
# X             self.edge(eid)

    def Tree(self, vid):
        g = self._g

        self.prev_node = tree_node = g.node(vid)
        props = g.get_vertex_property(vid)

        # self.spaces += 1
        self.xml_nodes[vid] = tree = xml.Element('Tree')
        tree.tail = '\n'
        tree.text = '\n'

        # Extract SegmentType & LeafType
        if 'SegmentType' in props:
            tree.attrib['SegmentType'] = props.pop('SegmentType')
        if 'LeafType' in props:
            tree.attrib['LeafType'] = props.pop('LeafType')

        # TreeAttributes: point, direction, LGA*
        ta = self.filter_attributes(props, fields=('point', 'direction'),
                                    pattern='LGA')
        self.attributes(tree, 'TreeAttributes', ta)

        # Tree Parameters : LGP*
        tp = self.filter_attributes(props, pattern='LGP')
        self.attributes(tree, 'TreeParameters', tp)

        # TreeFunctions: LGM*
        tf = self.filter_attributes(props, pattern='LGM')
        self.attributes(tree, 'TreeFunctions', tf)

        # Manage the recursive structure?
        self.trees.append(tree)

    def process_vertex(self, vid):
        g = self._g
        pid = g.parent(vid)
        cid = g.complex(vid)
        edge = g.edge_type(vid)
        scale = g.scale(vid)
        bp = self.branching_point

        prev_scale = self.prev_node.scale()
        if scale > prev_scale:
            # add simply the node to its complex
            xml_node = self.xml_nodes[cid]
            new_elt = self.add_element(xml_node, vid)
        elif (scale < prev_scale) or (scale == 2):
            # Add a new axis: test if + or not
            # if + retrieve the branching point element
            # else add to the tree
            if edge == '+':
                # Create or retrieve the BranchingPoint

                if pid in bp:
                    xml_node = bp[pid]
                else:
                    xml_node = self.xml_nodes[pid]
                    bp[pid] = bp_node = self.SubElement(xml_node, 'BranchingPoint')
                    self.SubElement(bp_node, 'BranchingPointAttributes')
                    xml_node = bp_node
            else:
                xml_node = self.xml_nodes[cid]

            # Add the Axis to the BranchingPoint
            new_elt = self.add_element(xml_node, vid)
        elif scale == 3:
            # Axis which have not been decomposed
            xml_node = self.xml_nodes[cid]
            new_elt = self.add_element(xml_node, vid)

        if scale == 3 and edge == '<':
            axis_id = cid
            # In this case, we have leaved the Branching
            # Then a new branching point have to be created on this Axis
            # at the next ramification
            if axis_id in bp:
                del bp[axis_id]

        self.xml_nodes[vid] = new_elt
        self.prev_node = g.node(vid)

    def add_element(self, xml_node, vid):
        g = self._g
        props = g.get_vertex_property(vid)
        tag = props['label']
        attrib = {}
        if tag in ('TreeSegment', 'Bud', 'BroadLeaf'):
            if 'ObjectIndex' in props:
                attrib['ObjectIndex'] = props.pop('ObjectIndex')
            if (tag == 'BroadLeaf') and ('Shape' in props):
                attrib['Shape'] = props.pop('Shape')
        # Create the Element
        new_elt = self.SubElement(xml_node, tag, attrib)

        fields = ['point', 'direction']
        if tag == 'BroadLeaf':
            fields += 'SkySectors PetioleStart PetioleEnd LeafNormal xdir ydir EllipseSMajorA EllipseSMinorA RadiationVector'.split()
        ta = self.filter_attributes(props, fields=fields,
                                    pattern='LGA')
        tag_attrib = props['label'] + 'Attributes'
        self.attributes(new_elt, tag_attrib, ta)

        return new_elt

    def attributes(self, node, tag, props, **attrib):
        # self.spaces += 1
        ta = self.SubElement(node, tag, attrib)
        # self.spaces += 1
        for k, v in props.iteritems():
            se = xml.SubElement(ta, k)
            se.text = v
            se.tail = '\n'
        # self.spaces-=2

    @staticmethod
    def filter_attributes(d, fields=[], pattern='LG'):
        attr = {}
        for k, v in d.iteritems():
            if k in fields or k.startswith(pattern):
                attr[k] = v
        return attr

    def universal_node(self):
        # test
        _types = self._graph._types
        # _types['Boid']=['sphere']
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

def lignum_turtle(g, property_name='LGAtype', cmap='jet', lognorm=False, has_color=False):
    """ Plot in 3D an MTG generated from LIGNUM XML Tree using a turtle.

    """
    import numpy as np
    def compute_color(g, _cmap, _lognorm):

        if not 'LGAtype' in g.properties():
            return g
        p = g.property('LGAtype')
        keys = p.keys()
        vs = p.values()
        if vs and isinstance(vs [0], str):
            try:
                values = np.array(vs,dtype='int')
            except ValueError:
                values = np.array(vs,dtype='float')

            g.properties()['LGAtype'] = dict(zip(keys, values))

        mtg_color.colormap(g, 'LGAtype', cmap=_cmap, lognorm=_lognorm)
        return g


    COLOR_SEGMENT = 1
    COLOR_LEAF = 2
    COLOR_BUD= 3
    PETIOL_RADIUS = 0.001
    BUD_SIZE = 0.01
    BUD_GEOM = pgl.Translated((0,0,BUD_SIZE),
                              pgl.Scaled((1/3.,1/3.,1), pgl.Sphere(radius=BUD_SIZE)))

    if not has_color:
        g = compute_color(g, _cmap=cmap, _lognorm=lognorm)

    # Define the global properties first:
    # Base diameter LGADbase
    n = g.node(1)
    position = Vector3(map(float,n.point.split()))

    myTurtle = pgl.PglTurtle()
    myTurtle.move(position)

    def lignum_visitor(g, v, turtle):
        n = g.node(v)
        turtle.setId(v)
        radius_factor = 1. if not g.parent(v) else 1.5

        def my_leaf(xs, ys):
            return pgl.Translated((xs/2,0,0),
                              pgl.Scaled((1,ys/xs,1), pgl.Disc(radius=xs/2)))
        def setDir(d):
            up = (d^turtle.getUp())^d
            turtle.setHead(direction, up)

        if n.label == 'TreeSegment':
            turtle.setColor(COLOR_SEGMENT)
            radius = float(n.LGAR)
            length = float(n.LGAL)
            position = Vector3(map(float,n.point.split()))
            direction = Vector3(map(float,n.direction.split()))

            turtle.move(position)
            turtle.setWidth(radius)

            if n.parent() is None:
                turtle.customGeometry(pgl.Disc(radius))

            setDir(direction)
            turtle.F(length)
            if n.parent() is None:
                turtle.customGeometry(pgl.Disc(radius))

        elif n.label == 'Bud':
            turtle.setColor(COLOR_BUD)
            position = Vector3(map(float,n.point.split()))
            direction = Vector3(map(float,n.direction.split()))
            turtle.move(position)
            setDir(direction)
            turtle.customGeometry(BUD_GEOM)
        elif n.label == 'BroadLeaf':
            petiol_start = Vector3(map(float,n.PetioleStart.split()))
            petiol_end = Vector3(map(float,n.PetioleEnd.split()))
            leaf_normal = Vector3(map(float,n.LeafNormal.split()))
            xdir = Vector3(map(float,n.xdir.split()))
            ydir = Vector3(map(float,n.ydir.split()))
            xsize = float(n.EllipseSMajorA)
            ysize = float(n.EllipseSMinorA)

            # petiol
            turtle.setColor(COLOR_SEGMENT)
            turtle.move(petiol_start)
            turtle.setWidth(PETIOL_RADIUS)
            turtle.lineTo(petiol_end)

            # leaf
            turtle.setColor(COLOR_LEAF)
            turtle.setHead(leaf_normal,xdir)
            turtle.customGeometry(my_leaf(xsize,ysize))


    scene = mtg_turtle.TurtleFrame(g,lignum_visitor,myTurtle, all_roots=True, gc=False)
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


def mtg2xml(graph, xml_file=''):
    """
    """
    dump = Dumper()
    s = dump.dump(graph)

    if not xml_file:
        fd, xml_file = mkstemp(suffix='.xml')
    f = open(xml_file, 'w')
    f.write(s)
    f.close()

    return xml_file


