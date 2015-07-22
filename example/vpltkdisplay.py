from IPython.display import Image, display
import tempfile, os
from openalea.plantgl.all import Viewer, Scene
from openalea.misc.dataflow_directive import run_code
from openalea.core.path import path

def PlantGL(scene):
    fn = tempfile.mktemp(suffix='.png')
    Viewer.frameGL.setBgColor(255,255,255)
    Viewer.animation(True)
    Viewer.display(scene)
    Viewer.saveSnapshot(fn, 'png')
    img = Image(fn)
    os.unlink(fn)
    return img

def Dataflow(pkg,node):
    temp_dir=tempfile.mkdtemp()
    options={}
    run_code(temp_dir,pkg,node,'',temp_dir,'.',options)
    img_name = os.path.join(temp_dir,('dataflow_'+node+'.png'))
    img = Image(img_name)
    #os.unlink(img_name)
    return img


