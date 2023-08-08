import bpy

class TrimNormalsPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trim Normals'
    bl_label = 'Trim Normals'

    def draw(self, context):
        col = self.layout.column()
        col.operator('opr.trim_normals_reset_operator', text='Reset Normals')
        col.operator('opr.trim_normals_adjust_operator', text='Adjust Normals')
        pass


def register():
    pass
