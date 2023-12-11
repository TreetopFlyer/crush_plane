import bpy
import bmesh
import mathutils
from mathutils import Vector
from mathutils import Matrix

def GetDirection(inObj):
        members = inObj.matrix_world.col
        normal = Vector((members[2][0], members[2][1], members[2][2]))
        normal.normalize()
        return normal
    
def GetPosition(inObj):
        members = inObj.matrix_world.col
        return Vector((members[3][0], members[3][1], members[3][2]))

def Crusher(obj, planePos, planeDir, projDir):
        mWorld = obj.matrix_world;
        mInverse = obj.matrix_world.inverted()
        dot_product = projDir.dot(planeDir)
        def _Crusher(inVector):
            outVector = mWorld @ inVector
            if abs(dot_product) > 1e-6:
                t = (planePos - outVector).dot(planeDir) / dot_product
                outVector = outVector + projDir * t
            return mInverse @ outVector
        return _Crusher

def CrushSelection(inCrusher):
    mesh = bmesh.from_edit_mesh(bpy.context.object.data)
    for vert in mesh.verts:
        if vert.select:      
            vert.co = inCrusher(vert.co)
    bmesh.update_edit_mesh(bpy.context.object.data)   

plane = D.objects['Plane']    
arrow = D.objects['Arrow']
crush = Crusher(C.object, GetPosition(plane), GetDirection(plane), GetDirection(arrow))
CrushSelection(crush)