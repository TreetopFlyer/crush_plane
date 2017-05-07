bl_info = {
    "name": "Crush Plane",
    "category": "Object",
}

import bpy
import bmesh
import mathutils
from mathutils import Vector

class CrushPlane:

    PlaneVector = Vector((0, 0.7, 0.7))
    PlaneOffset = 0
    ProjectVector = Vector((0, 0, -1))

    def SetPlane(inMesh):
        three = []
        mesh = bmesh.from_edit_mesh(inMesh)
        for vert in mesh.verts:
            if vert.select:
                three.append(vert.co)
                if(len(three) == 3):
                    
                    three[1] = three[1] - three[0]
                    three[2] = three[2] - three[0]
                    
                    
                    CrushPlane.PlaneVector = three[1].cross(three[2])
                    CrushPlane.PlaneVector.normalize()
                    CrushPlane.PlaneOffset = three[0].dot(CrushPlane.PlaneVector)
                    
                    return
        print("Not Enough Verticies selcted for plane")

    def SetProjection(inMesh):
        two = []
        mesh = bmesh.from_edit_mesh(inMesh)
        for vert in mesh.verts:
            if vert.select:
                two.append(vert.co)
                if(len(two) == 2):
                    CrushPlane.ProjectVector = two[1] - two[0]
                    print(CrushPlane.ProjectVector)
                    return
                
        print("Not Enough Verticies selcted for projection")
        
    def SetPlaneOffset(inMesh):
        mesh = bmesh.from_edit_mesh(inMesh)
        for vert in mesh.verts:
            if vert.select:
                CrushPlane.PlaneOffset = vert.co.dot(CrushPlane.PlaneVector)
                return
    
    def CrushVertex(inVertex):
        vOther = inVertex.co + CrushPlane.ProjectVector
        dVertex = inVertex.co.dot(CrushPlane.PlaneVector) - CrushPlane.PlaneOffset
        dOther = vOther.dot(CrushPlane.PlaneVector) - CrushPlane.PlaneOffset
        dSum = dVertex - dOther
        dPercent = dVertex/dSum
        inVertex.co.x = inVertex.co.x + dPercent*(vOther.x - inVertex.co.x)
        inVertex.co.y = inVertex.co.y + dPercent*(vOther.y - inVertex.co.y)
        inVertex.co.z = inVertex.co.z + dPercent*(vOther.z - inVertex.co.z)

    def CrushVerticies(inMesh):
        mesh = bmesh.from_edit_mesh(inMesh)
        for vert in mesh.verts:
            if vert.select:
                CrushPlane.CrushVertex(vert)
        bmesh.update_edit_mesh(inMesh)

###########################

class CrushPlaneCrush(bpy.types.Operator):
    """Crush verticies onto a plane along a direction"""
    bl_idname = "mesh.crush_plane_crush"
    bl_label = "Crush Plane: Crush"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.CrushVerticies(context.active_object.data)
        return {'FINISHED'}

class CrushPlaneSetPlane(bpy.types.Operator):
    """Infer the crush plane from selected geometry"""
    bl_idname = "mesh.crush_plane_set_plane"
    bl_label = "Crush Plane: Set Plane"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.SetPlane(context.active_object.data)
        return {'FINISHED'}

class CrushPlaneSetPlaneOffset(bpy.types.Operator):
    """Move the crush plane to the selected vertex"""
    bl_idname = "mesh.crush_plane_set_plane_offset"
    bl_label = "Crush Plane: Set Plane Offset"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.SetPlaneOffset(context.active_object.data)
        return {'FINISHED'}

class CrushPlaneSetProjection(bpy.types.Operator):
    """Infer the crush plane projection from selected geometry"""
    bl_idname = "mesh.crush_plane_set_projection"
    bl_label = "Crush Plane: Set Projection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.SetProjection(context.active_object.data)
        return {'FINISHED'}

class CrushPlaneSetProjectionZ(bpy.types.Operator):
    """Crush along local Z"""
    bl_idname = "mesh.crush_plane_set_projection_z"
    bl_label = "Crush Plane: Set Projection Z"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.ProjectVector = Vector((0, 0, 1))
        return {'FINISHED'}
    
class CrushPlaneSetProjectionY(bpy.types.Operator):
    """Crush along local Y"""
    bl_idname = "mesh.crush_plane_set_projection_y"
    bl_label = "Crush Plane: Set Projection Y"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.ProjectVector = Vector((0, 1, 0))
        return {'FINISHED'}
    
class CrushPlaneSetProjectionX(bpy.types.Operator):
    """Crush along local X"""
    bl_idname = "mesh.crush_plane_set_projection_x"
    bl_label = "Crush Plane: Set Projection X"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.ProjectVector = Vector((1, 0, 0))
        return {'FINISHED'}

class CrushPlaneUI(bpy.types.Panel):

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Crush Plane"
    bl_idname = "VIEW3D_PT_crush_plane"
    bl_context = "mesh_edit"
    bl_category = "Tools"

    def draw(self, context):
        
        layout = self.layout
        obj = context.object

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("mesh.crush_plane_set_plane", text="Get Plane From")
        row.operator("mesh.crush_plane_set_plane_offset", text="Move Plane To")
        
        col = layout.column(align=True)
        
        col.operator("mesh.crush_plane_set_projection", text="Get Projection")
        row = col.row(align=True)
        row.operator("mesh.crush_plane_set_projection_x", text="X")
        row.operator("mesh.crush_plane_set_projection_y", text="Y")
        row.operator("mesh.crush_plane_set_projection_z", text="Z")
        
        col = layout.column(align=True)
        col.operator("mesh.crush_plane_crush", text="Crush")


def register():
    bpy.utils.register_class(CrushPlaneCrush)
    bpy.utils.register_class(CrushPlaneSetPlane)
    bpy.utils.register_class(CrushPlaneSetPlaneOffset)
    bpy.utils.register_class(CrushPlaneSetProjection)
    bpy.utils.register_class(CrushPlaneSetProjectionX)
    bpy.utils.register_class(CrushPlaneSetProjectionY)
    bpy.utils.register_class(CrushPlaneSetProjectionZ)
    bpy.utils.register_class(CrushPlaneUI)


def unregister():
    bpy.utils.unregister_class(CrushPlaneCrush)
    bpy.utils.unregister_class(CrushPlaneSetPlane)
    bpy.utils.unregister_class(CrushPlaneSetOffset)
    bpy.utils.unregister_class(CrushPlaneSetProjection)
    bpy.utils.unregister_class(CrushPlaneSetProjectionX)
    bpy.utils.unregister_class(CrushPlaneSetProjectionY)
    bpy.utils.unregister_class(CrushPlaneSetProjectionZ)
    bpy.utils.unregister_class(CrushPlaneUI)



if __name__ == "__main__":
    register()