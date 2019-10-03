bl_info = {
    "name": "Crush Plane",
    "author": "Seth Trowbidge",
    "version": (2, 0, 0),
    "blender": (2, 8, 0),
    "location": "Edit Mesh > Tools > Crush Plane",
    "description": ("Work with planes in edit mesh mode"),
    "warning": "",  # used for warning icon and text in addons panel
    "category": "Mesh"}

import bpy
import bmesh
import mathutils
from mathutils import Vector
from mathutils import Matrix

class CrushPlane:

    VectorProject = Vector((0, 0, -1))
    VectorCustom = Vector((0, 0, -1))

    PlaneOffset = 0
    PlaneVector = Vector((0, 0, 1))

    DrawPlaneName = "CrushPlane Plane"
    DrawPlane = False

    def SetupPlane():
        CrushPlane.DrawPlane = bpy.data.objects.new(CrushPlane.DrawPlaneName, None )
        bpy.context.scene.collection.objects.link( CrushPlane.DrawPlane )
        CrushPlane.DrawPlane.empty_display_type = 'IMAGE'
        CrushPlane.DrawPlane.empty_image_offset = [-0.5, -0.5]
        CrushPlane.DrawPlane.empty_display_size = 3
        
    def ShowPlane():
        bpy.context.scene.collection.objects.link(CrushPlane.DrawPlane)
    
    def HidePlane():
        bpy.context.scene.collection.objectsunlink(CrushPlane.DrawPlane)


    def GetNormal():
        members = CrushPlane.DrawPlane.matrix_world.col
        normal = Vector((members[2][0], members[2][1], members[2][2]))
        normal.normalize()
        return normal
    
    def GetPosition():
        members = CrushPlane.DrawPlane.matrix_world.col
        return Vector((members[3][0], members[3][1], members[3][2]))

    def SetPlane(inObject):
        three = []
        mesh = bmesh.from_edit_mesh(inObject.data)
        for vert in mesh.verts:
            if vert.select:
                three.append(inObject.matrix_world @ vert.co)
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
                two.append(inObject.matrix_world @ vert.co)
                if(len(two) == 2):
                    CrushPlane.VectorCustom = two[1] - two[0]
                    return
                
        print("Not Enough Verticies selcted for projection")
        
    def SetPlaneOffset(inObject):
        mesh = bmesh.from_edit_mesh(inObject.data)
        for vert in mesh.verts:
            if vert.select:
                one = inObject.matrix_world @ vert.co
                
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
                
                normal = CrushPlane.GetNormal()
                offset = CrushPlane.GetPosition().dot(normal)
                
                worldSpace = inObject.matrix_world @ vert.co
                vOther = worldSpace + CrushPlane.VectorProject
                dVertex = worldSpace.dot(normal) - offset
                dOther = vOther.dot(normal) - offset
                dSum = dVertex - dOther
                dPercent = dVertex/dSum
                worldSpace.x = worldSpace.x + dPercent*(vOther.x - worldSpace.x)
                worldSpace.y = worldSpace.y + dPercent*(vOther.y - worldSpace.y)
                worldSpace.z = worldSpace.z + dPercent*(vOther.z - worldSpace.z)
                
                vert.co = inverse @ worldSpace
                
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
        CrushPlane.VectorProject = CrushPlane.VectorCustom.copy();
        CrushPlane.CrushVerticies(context.active_object)
        return {'FINISHED'}

class CrushPlaneCrushZ(bpy.types.Operator):
    """Crush along local Z"""
    bl_idname = "mesh.crush_plane_crush_z"
    bl_label = "Crush Plane: Crush Z"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.VectorProject = Vector((0, 0, 1))
        CrushPlane.CrushVerticies(context.active_object)
        return {'FINISHED'}
    
class CrushPlaneCrushY(bpy.types.Operator):
    """Crush along local Y"""
    bl_idname = "mesh.crush_plane_crush_y"
    bl_label = "Crush Plane: Crush Y"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.VectorProject = Vector((0, 1, 0))
        CrushPlane.CrushVerticies(context.active_object)
        return {'FINISHED'}
    
class CrushPlaneCrushX(bpy.types.Operator):
    """Crush along local X"""
    bl_idname = "mesh.crush_plane_crush_x"
    bl_label = "Crush Plane: Crush X"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        CrushPlane.VectorProject = Vector((1, 0, 0))
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
    
########

class CrushPlaneUI(bpy.types.Panel):

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Crush Plane"
    bl_idname = "VIEW3D_PT_crush_plane"
    bl_context = "mesh_edit"
    bl_category = "Tools"

    def draw(self, context):
        
        layout = self.layout
        obj = context.object

        if(CrushPlane.DrawPlaneName not in bpy.data.objects):
            col = layout.column(align=True)
            col.operator("mesh.crush_plane_setup_plane", text="Setup")
            
        else:
            col = layout.column(align=True)
            if(CrushPlane.DrawPlaneName not in bpy.context.scene.objects):
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


def register():

    bpy.utils.register_class(CrushPlaneSetupPlane)
    bpy.utils.register_class(CrushPlaneShowPlane)
    bpy.utils.register_class(CrushPlaneHidePlane)
    bpy.utils.register_class(CrushPlaneSetPlane)
    bpy.utils.register_class(CrushPlaneSetPlaneOffset)
    bpy.utils.register_class(CrushPlaneSetProjection)
    bpy.utils.register_class(CrushPlaneCrushCustom)
    bpy.utils.register_class(CrushPlaneCrushX)
    bpy.utils.register_class(CrushPlaneCrushY)
    bpy.utils.register_class(CrushPlaneCrushZ)
    bpy.utils.register_class(CrushPlaneBisect)
    bpy.utils.register_class(CrushPlaneUI)


def unregister():
    
    bpy.utils.unregister_class(CrushPlaneSetupPlane)
    bpy.utils.unregister_class(CrushPlaneShowPlane)
    bpy.utils.unregister_class(CrushPlaneHidePlane)
    bpy.utils.unregister_class(CrushPlaneSetPlane)
    bpy.utils.unregister_class(CrushPlaneSetPlaneOffset)
    bpy.utils.unregister_class(CrushPlaneSetProjection)
    bpy.utils.unregister_class(CrushPlaneCrushCustom)
    bpy.utils.unregister_class(CrushPlaneCrushX)
    bpy.utils.unregister_class(CrushPlaneCrushY)
    bpy.utils.unregister_class(CrushPlaneCrushZ)
    bpy.utils.unregister_class(CrushPlaneBisect)
    bpy.utils.unregister_class(CrushPlaneUI)



if __name__ == "__main__":
    register()  