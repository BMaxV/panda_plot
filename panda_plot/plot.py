from panda3d.core import *  # contains render2d somehow

from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectScrolledFrame

#necessary for geometry creation.
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import Geom, GeomTriangles,GeomTrifans, GeomVertexWriter
from panda3d.core import Texture, GeomNode

import random
import math

class Wrapper:
    def __init__(self):

        # this is required for this demo
        self.b = ShowBase()

        # this is sort of optional allows for easily building and deleting
        # elements
        self.UI_elements = []
        
    
    def build(self,directly=False):
        
        #panda_interface_glue.draw_shape_2d([(0,0,0),(1,1,0),(1,1.1,0),(0,0.1,0)])
        #return
        
        
        xs,ys,ys2,ys3=three_graphs()
        
        elements=[]
        elements+=convert_graph(xs,ys,z_offset=0)
        elements+=convert_graph(xs,ys2,z_offset=0.2)
        elements+=convert_graph(xs,ys3,z_offset=0.4)
    
        
        if directly:
            for path in elements:
                path.reparent_to(render2d)
            self.UI_elements=elements
            
        else:
            
            canvasSize1=(-0.5,0.5,-0,0.8)
            myframe = DirectScrolledFrame(canvasSize=canvasSize1, frameSize=(-.8, .8, 0, .4))
            myframe.setPos(-0.3, 0, -0.3)
            canvas=myframe.getCanvas()
            
            for path in elements:
                path.reparent_to(canvas)
            
            self.UI_elements=[myframe]
        
    def clean(self):
        """delete all elements"""
        for x in self.UI_elements:
            x.removeNode()
        self.UI_elements = []

def convert_graph(xs,ys,z_offset=0,thick=0.2):
    elements=[]
    m=len(xs)
    c=0
    thick=0.02
    while c < m-1:
        p1=(xs[c],z_offset,ys[c])
        p11=(xs[c],z_offset,ys[c] + thick)
        p2=(xs[c+1],z_offset,ys[c+1])
        p21=(xs[c+1],z_offset,ys[c+1] + thick)
        verts=[p1,p2,p21,p11]
        
        faces=[[0,1,2,3]]
        
        poly=makecoloredPoly(verts,faces)
        
        snode = GeomNode('Object1')
        snode.addGeom(poly)
        
        path=NodePath(snode)
        
        elements.append(path)
        
        c+=1
    return elements


def three_graphs():
    points=[(0,0,0),(1,1,0),(1,1.1,0),(0,0.1,0)]
        
    xs=[]
    ys=[]
    ys2=[]
    ys3=[]
    x=0
    fac=0.1
    while x < 5:
        xs.append((x)*fac)
        ys.append((1.5*x+0.5 +random.random())*fac )
        ys2.append((4+random.random())*fac)
        ys3.append((0.2*(x-2)**2+0.5)*fac)
        x+=1
    return xs,ys,ys2,ys3

def calculate_center(point_list):
    center_p=[0,0,0]
    for p in point_list:
        center_p[0]+=p[0]
        center_p[1]+=p[1]
        center_p[2]+=p[2]
    center_p[0]=center_p[0]/len(point_list)
    center_p[1]=center_p[1]/len(point_list)
    center_p[2]=center_p[2]/len(point_list)
    return center_p


def makecoloredPoly(verts,faces,color_tuple=None):
    """this function creates the polygon that will be added to the geom
    datastructure"""
    verts=verts.copy()
    # panda can not by itself create n-gons, it does support
    # "triangle fans" however, a set of triangles with
    # a shared center vertex.
    # this center has to be calculated first.
    
    old_vert_len=len(verts)
    
    #calculate the center first
    center_ids=[]
    for f in faces:
        vl=[]
        
        for p in f:
            vl.append(verts[p])
        center_p=calculate_center(vl)
        
        verts.append(center_p)
        center_ids.append(len(verts)-1)
    
    tformat=GeomVertexFormat.getV3t2()
    
    #this is the format we'll be using.
    format = GeomVertexFormat.getV3n3c4()
    vdata = GeomVertexData('convexPoly', format, Geom.UHStatic)

    vdata.setNumRows(len(verts))
    
    #these are access shortcuts
    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')
    
    #tells the format how many vertices we'll create
    
    if color_tuple==None:
        vran1=random.random()
        vran2=random.random()
        #color_t=random.choice([(255*random.random(),0,0),(0,255*random.random(),0)])#,(0,0,255)])
        color_t=(1*vran1,1*vran2,0)#,(0,255*random.random(),0)])#,
        #color_t=(0,0,255)
    else:
        color_t=color_tuple
        
    #set the data for each vertex.
    for p in verts:
        #color_t=random.choice([(255,0,0),(0,255,0),(0,0,255)])
        #color_t=(255,255,0)
        vertex.addData3(p[0],p[1],p[2])
        color.addData4f(*color_t[:],0.5)
        normal.addData3(0,0,1)
        #do i need normals?
    
    #this creates the geometry from the data.
    #or rather, this creates a geom object, with the vertex data
    #but in panda, nothing exists yet.
    poly = Geom(vdata)
    
    
    #this loop tells panda which verts in the vdata structure to
    #use to create the triangles
    c=0
    flb=0
    while c < len(faces):
        
        tris = GeomTrifans(Geom.UHStatic)
        #i.e. this face gets added.
        face=faces[c]
        
        #this would skip face #10
        #keeping it here for easy/easier debugging
        #if c==10:
        #    c+=1
        #    continue
        
        tris.addVertex(center_ids[c])
        for i in face:
            tris.addVertex(i)
        tris.addVertices(face[-1],face[0])
        tris.closePrimitive()
        poly.addPrimitive(tris)
        flb+=len(face)
        c+=1
    
    return poly


def main():
    W = Wrapper()
    W.build(True)

    while True:
        W.b.taskMgr.step()


if __name__ == "__main__":
    main()
