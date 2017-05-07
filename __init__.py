bl_info = {
    "name": "Crush Plane",
    "category": "Object",
}

import bpy
import bmesh
import mathutils
from mathutils import Vector

class CrushPlane:

    PlaneVector = Vector((0, 0.0, 1))
    PlaneOffset = 0
    ProjectVector = Vector((0, 0, -1))
    CustomVector = Vector((0, 0, -1))

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
                    CrushPlane.CustomVector = two[1] - two[0]
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

class CrushPlaneCrushCustom(bpy.types.Operator):
    """Crush verticies onto a plane along a direction"""
    bl_idname = "mesh.crush_plane_crush_custom"
    bl_label = "Crush Plane: Crush"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.ProjectVector = CrushPlane.CustomVector.copy();
        CrushPlane.CrushVerticies(context.active_object.data)
        return {'FINISHED'}

class CrushPlaneCrushZ(bpy.types.Operator):
    """Crush along local Z"""
    bl_idname = "mesh.crush_plane_crush_z"
    bl_label = "Crush Plane: Crush Z"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.ProjectVector = Vector((0, 0, 1))
        CrushPlane.CrushVerticies(context.active_object.data)
        return {'FINISHED'}
    
class CrushPlaneCrushY(bpy.types.Operator):
    """Crush along local Y"""
    bl_idname = "mesh.crush_plane_crush_y"
    bl_label = "Crush Plane: Crush Y"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.ProjectVector = Vector((0, 1, 0))
        CrushPlane.CrushVerticies(context.active_object.data)
        return {'FINISHED'}
    
class CrushPlaneCrushX(bpy.types.Operator):
    """Crush along local X"""
    bl_idname = "mesh.crush_plane_crush_x"
    bl_label = "Crush Plane: Crush X"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.ProjectVector = Vector((1, 0, 0))
        CrushPlane.CrushVerticies(context.active_object.data)
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
        row.operator("mesh.crush_plane_set_plane", text="Get Plane")
        row.operator("mesh.crush_plane_set_plane_offset", text="Move Plane")
        row.operator("mesh.crush_plane_set_projection", text="Get Custom Projection")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("mesh.crush_plane_crush_x", text="X")
        row.operator("mesh.crush_plane_crush_y", text="Y")
        row.operator("mesh.crush_plane_crush_z", text="Z")
        row.operator("mesh.crush_plane_crush_custom", text="Custom")


def register():
    
    bpy.utils.register_class(CrushPlaneSetPlane)
    bpy.utils.register_class(CrushPlaneSetPlaneOffset)
    bpy.utils.register_class(CrushPlaneSetProjection)
    bpy.utils.register_class(CrushPlaneCrushCustom)
    bpy.utils.register_class(CrushPlaneCrushX)
    bpy.utils.register_class(CrushPlaneCrushY)
    bpy.utils.register_class(CrushPlaneCrushZ)
    bpy.utils.register_class(CrushPlaneUI)


def unregister():
    
    bpy.utils.unregister_class(CrushPlaneSetPlane)
    bpy.utils.unregister_class(CrushPlaneSetPlaneOffset)
    bpy.utils.unregister_class(CrushPlaneSetProjection)
    bpy.utils.unregister_class(CrushPlaneCrushCustom)
    bpy.utils.unregister_class(CrushPlaneCrushX)
    bpy.utils.unregister_class(CrushPlaneCrushY)
    bpy.utils.unregister_class(CrushPlaneCrushZ)
    bpy.utils.unregister_class(CrushPlaneUI)



if __name__ == "__main__":
    register()