bl_info = {
    "name": "Crush Plane",
    "author": "Seth Trowbidge",
    "version": (2, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Edit Mesh > Crush Plane",
    "description": "Work with planes in edit mesh mode",
    "warning": ""
}

import bpy
import bmesh
import mathutils
from mathutils import Vector
from mathutils import Matrix

class CrushPlane:
    ProjectVector = Vector((0, 0, -1))
    CustomVector = Vector((0, 0, -1))

    DrawPlaneName = "CrushPlane Plane"
    DrawPlane = None

    @classmethod
    def SetupPlane(cls):
        cls.DrawPlane = bpy.data.objects.new(cls.DrawPlaneName, None)
        cls.DrawPlane.empty_display_type = 'IMAGE'
        cls.DrawPlane.empty_image_offset = [-0.5, -0.5]
        cls.DrawPlane.empty_display_size = 3
        
    @classmethod
    def ShowPlane(cls):
        bpy.context.collection.objects.link(cls.DrawPlane)
    
    @classmethod
    def HidePlane(cls):
        bpy.context.collection.objects.unlink(cls.DrawPlane)

    @classmethod
    def GetNormal(cls):
        members = cls.DrawPlane.matrix_world.col
        normal = Vector((members[2][0], members[2][1], members[2][2]))
        normal.normalize()
        return normal
    
    @classmethod
    def GetPosition(cls):
        members = cls.DrawPlane.matrix_world.col
        return Vector((members[3][0], members[3][1], members[3][2]))

    @classmethod
    def SetPlane(cls, inObject):
        three = []
        mesh = bmesh.from_edit_mesh(inObject.data)
        for vert in mesh.verts:
            if vert.select:
                three.append(inObject.matrix_world @ vert.co)
                if len(three) == 3:
                    
                    three[1] = three[1] - three[0]
                    three[2] = three[2] - three[0]
                    
                    cls.PlaneVector = three[1].cross(three[2])
                    cls.PlaneVector.normalize()
                    cls.DrawPlane.matrix_world = Matrix.Translation(three[0])
                    
                    vZ = cls.PlaneVector
                    vY = three[1]
                    vY.normalize()
                    vX = three[1].cross(cls.PlaneVector)
                    
                    cls.DrawPlane.matrix_world.col[2][0] = vZ.x
                    cls.DrawPlane.matrix_world.col[2][1] = vZ.y
                    cls.DrawPlane.matrix_world.col[2][2] = vZ.z
                    
                    cls.DrawPlane.matrix_world.col[1][0] = vY.x
                    cls.DrawPlane.matrix_world.col[1][1] = vY.y
                    cls.DrawPlane.matrix_world.col[1][2] = vY.z
                    
                    cls.DrawPlane.matrix_world.col[0][0] = -vX.x
                    cls.DrawPlane.matrix_world.col[0][1] = -vX.y
                    cls.DrawPlane.matrix_world.col[0][2] = -vX.z
                    
                    return
        print("Not Enough Vertices selected for plane")

    @classmethod
    def SetProjection(cls, inObject):
        two = []
        mesh = bmesh.from_edit_mesh(inObject.data)
        for vert in mesh.verts:
            if vert.select:
                two.append(inObject.matrix_world @ vert.co)
                if len(two) == 2:
                    cls.CustomVector = two[1] - two[0]
                    return
                
        print("Not Enough Vertices selected for projection")
        
    @classmethod
    def SetPlaneOffset(cls, inObject):
        mesh = bmesh.from_edit_mesh(inObject.data)
        for vert in mesh.verts:
            if vert.select:
                one = inObject.matrix_world @ vert.co
                
                cls.DrawPlane.matrix_world.col[3][0] = one.x
                cls.DrawPlane.matrix_world.col[3][1] = one.y
                cls.DrawPlane.matrix_world.col[3][2] = one.z
                
                cls.PlaneOffset = one.dot(cls.PlaneVector)
                return

    @classmethod
    def CrushVerticies(cls, inObject): 
        inverse = inObject.matrix_world.inverted()
        mesh = bmesh.from_edit_mesh(inObject.data)
        for vert in mesh.verts:
            if vert.select:
                
                normal = cls.GetNormal()
                offset = cls.GetPosition().dot(normal)
                
                worldSpace = inObject.matrix_world @ vert.co
                vOther = worldSpace + cls.ProjectVector
                dVertex = worldSpace.dot(normal) - offset
                dOther = vOther.dot(normal) - offset
                dSum = dVertex - dOther
                dPercent = dVertex/dSum
                worldSpace.x = worldSpace.x + dPercent*(vOther.x - worldSpace.x)
                worldSpace.y = worldSpace.y + dPercent*(vOther.y - worldSpace.y)
                worldSpace.z = worldSpace.z + dPercent*(vOther.z - worldSpace.z)
                
                vert.co = inverse @ worldSpace
                
        bmesh.update_edit_mesh(inObject.data)


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
    """Crush vertices onto a plane along a direction"""
    bl_idname = "mesh.crush_plane_crush_custom"
    bl_label = "Crush Plane: Crush"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.ProjectVector = CrushPlane.CustomVector.copy()
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
    
class CrushPlaneBisect(bpy.types.Operator):
    """Bisect with crush plane"""
    bl_idname = "mesh.crush_plane_bisect"
    bl_label = "Crush Plane: Bisect"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.mesh.bisect(plane_co=CrushPlane.GetPosition(), plane_no=CrushPlane.GetNormal())
        return {'FINISHED'}
    
class CrushPlaneSetupPlane(bpy.types.Operator):
    """Generate cut plane object"""
    bl_idname = "mesh.crush_plane_setup_plane"
    bl_label = "Crush Plane: Setup Plane"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.SetupPlane()
        return {'FINISHED'}

class CrushPlaneShowPlane(bpy.types.Operator):
    """Add cut plane to scene"""
    bl_idname = "mesh.crush_plane_show_plane"
    bl_label = "Crush Plane: Show Plane"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.ShowPlane()
        return {'FINISHED'}
    
class CrushPlaneHidePlane(bpy.types.Operator):
    """Remove cut plane from scene"""
    bl_idname = "mesh.crush_plane_hide_plane"
    bl_label = "Crush Plane: Hide Plane"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.HidePlane()
        return {'FINISHED'}
    
class CrushPlaneUI(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Crush'
    bl_label = 'Crush Plane Tools'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        
        if CrushPlane.DrawPlaneName not in bpy.data.objects:
            col = layout.column(align=True)
            col.operator("mesh.crush_plane_setup_plane", text="Setup")
            
        else:
            col = layout.column(align=True)
            if CrushPlane.DrawPlaneName not in bpy.context.scene.collection.objects:
                col.operator("mesh.crush_plane_show_plane", text="Show Plane")
            else:
                col.operator("mesh.crush_plane_hide_plane", text="Hide Plane")
            
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
            
            col = layout.column(align=True)
            col.operator("mesh.crush_plane_bisect", text="Bisect")



classes = [
    CrushPlaneSetupPlane,
    CrushPlaneShowPlane,
    CrushPlaneHidePlane,
    CrushPlaneSetPlane,
    CrushPlaneSetPlaneOffset,
    CrushPlaneSetProjection,
    CrushPlaneCrushCustom,
    CrushPlaneCrushX,
    CrushPlaneCrushY,
    CrushPlaneCrushZ,
    CrushPlaneBisect,
    CrushPlaneUI
]

def classes_unregister():
    for item in classes:
        bpy.utils.unregister_class(item)

def register():
    for item in classes:
        bpy.utils.register_class(item)

def unregister():
    for item in classes:
        bpy.utils.unregister_class(item)

if __name__ == "__main__":
    register()
