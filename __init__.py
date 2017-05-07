bl_info = {
    "name": "Crush Plane",
    "category": "Object",
}

import bpy
import bmesh
import mathutils
from mathutils import Vector
from mathutils import Matrix

class CrushPlane:

    PlaneMatrix = Matrix.Translation((0, 0, 0))
    ProjectVector = Vector((0, 0, -1))
    CustomVector = Vector((0, 0, -1))
    
    DrawPlane = bpy.data.objects.new("CrushPlane Plane", None )
    DrawPlane.empty_draw_type = 'IMAGE'
    bpy.context.scene.objects.link(DrawPlane)

    def GetNormal():
        members = CrushPlane.DrawPlane.matrix_world.col
        normal = Vector((members[2][0], members[2][1], members[2][2], 0))
        normal.normalize()
        position = Vector((members[3][0], members[3][1], members[3][2]))
        normal.w = -position.dot(normal)
        return normal

    def SetPlane(inObject):
        three = []
        mesh = bmesh.from_edit_mesh(inObject.data)
        for vert in mesh.verts:
            if vert.select:
                three.append(inObject.matrix_world * vert.co)
                if(len(three) == 3):
                    
                    three[1] = three[1] - three[0]
                    three[2] = three[2] - three[0]
                    
                    CrushPlane.PlaneVector = three[1].cross(three[2])
                    CrushPlane.PlaneVector.normalize()
                    CrushPlane.DrawPlane.matrix_world = Matrix.Translation(three[0])
                    
                    vZ = CrushPlane.PlaneVector
                    vY = three[1]
                    vY.normalize()
                    vX = three[1].cross(CrushPlane.PlaneVector)
                    
                    CrushPlane.DrawPlane.matrix_world.col[2][0] = vZ.x
                    CrushPlane.DrawPlane.matrix_world.col[2][1] = vZ.y
                    CrushPlane.DrawPlane.matrix_world.col[2][2] = vZ.z
                    
                    CrushPlane.DrawPlane.matrix_world.col[1][0] = vY.x
                    CrushPlane.DrawPlane.matrix_world.col[1][1] = vY.y
                    CrushPlane.DrawPlane.matrix_world.col[1][2] = vY.z
                    
                    CrushPlane.DrawPlane.matrix_world.col[0][0] = -vX.x
                    CrushPlane.DrawPlane.matrix_world.col[0][1] = -vX.y
                    CrushPlane.DrawPlane.matrix_world.col[0][2] = -vX.z
                    
                    return
        print("Not Enough Verticies selcted for plane")

    def SetProjection(inObject):
        two = []
        mesh = bmesh.from_edit_mesh(inObject.data)
        for vert in mesh.verts:
            if vert.select:
                two.append(inObject.matrix_world * vert.co)
                if(len(two) == 2):
                    CrushPlane.CustomVector = two[1] - two[0]
                    return
                
        print("Not Enough Verticies selcted for projection")
        
    def SetPlaneOffset(inObject):
        mesh = bmesh.from_edit_mesh(inObject.data)
        for vert in mesh.verts:
            if vert.select:
                one = inObject.matrix_world * vert.co
                
                CrushPlane.DrawPlane.matrix_world.col[3][0] = one.x
                CrushPlane.DrawPlane.matrix_world.col[3][1] = one.y
                CrushPlane.DrawPlane.matrix_world.col[3][2] = one.z
                
                CrushPlane.PlaneOffset = one.dot(CrushPlane.PlaneVector)
                return

    #####

    def CrushVerticies(inObject): 
        inverse = inObject.matrix_world.inverted()
        mesh = bmesh.from_edit_mesh(inObject.data)
        for vert in mesh.verts:
            if vert.select:
                
                parts = CrushPlane.GetNormal()
                
                worldSpace = inObject.matrix_world * vert.co
                vOther = worldSpace + CrushPlane.ProjectVector
                dVertex = worldSpace.dot(Vector((parts.x, parts.y, parts.z))) + parts.w
                dOther = vOther.dot(Vector((parts.x, parts.y, parts.z))) + parts.w
                dSum = dVertex - dOther
                dPercent = dVertex/dSum
                worldSpace.x = worldSpace.x + dPercent*(vOther.x - worldSpace.x)
                worldSpace.y = worldSpace.y + dPercent*(vOther.y - worldSpace.y)
                worldSpace.z = worldSpace.z + dPercent*(vOther.z - worldSpace.z)
                
                vert.co = inverse * worldSpace
                
        bmesh.update_edit_mesh(inObject.data)

###########################


class CrushPlaneSetPlane(bpy.types.Operator):
    """Infer the crush plane from selected geometry"""
    bl_idname = "mesh.crush_plane_set_plane"
    bl_label = "Crush Plane: Set Plane"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.SetPlane(context.active_object)
        return {'FINISHED'}

class CrushPlaneSetPlaneOffset(bpy.types.Operator):
    """Move the crush plane to the selected vertex"""
    bl_idname = "mesh.crush_plane_set_plane_offset"
    bl_label = "Crush Plane: Set Plane Offset"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.SetPlaneOffset(context.active_object)
        return {'FINISHED'}

class CrushPlaneSetProjection(bpy.types.Operator):
    """Infer the crush plane projection from selected geometry"""
    bl_idname = "mesh.crush_plane_set_projection"
    bl_label = "Crush Plane: Set Projection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.SetProjection(context.active_object)
        return {'FINISHED'}

class CrushPlaneCrushCustom(bpy.types.Operator):
    """Crush verticies onto a plane along a direction"""
    bl_idname = "mesh.crush_plane_crush_custom"
    bl_label = "Crush Plane: Crush"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.ProjectVector = CrushPlane.CustomVector.copy();
        CrushPlane.CrushVerticies(context.active_object)
        return {'FINISHED'}

class CrushPlaneCrushZ(bpy.types.Operator):
    """Crush along local Z"""
    bl_idname = "mesh.crush_plane_crush_z"
    bl_label = "Crush Plane: Crush Z"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.ProjectVector = Vector((0, 0, 1))
        CrushPlane.CrushVerticies(context.active_object)
        return {'FINISHED'}
    
class CrushPlaneCrushY(bpy.types.Operator):
    """Crush along local Y"""
    bl_idname = "mesh.crush_plane_crush_y"
    bl_label = "Crush Plane: Crush Y"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.ProjectVector = Vector((0, 1, 0))
        CrushPlane.CrushVerticies(context.active_object)
        return {'FINISHED'}
    
class CrushPlaneCrushX(bpy.types.Operator):
    """Crush along local X"""
    bl_idname = "mesh.crush_plane_crush_x"
    bl_label = "Crush Plane: Crush X"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.ProjectVector = Vector((1, 0, 0))
        CrushPlane.CrushVerticies(context.active_object)
        return {'FINISHED'}

########

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