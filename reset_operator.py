import bpy
              
class TrimNormalsResetOperator(bpy.types.Operator):
    bl_idname = 'opr.trim_normals_reset_operator'
    bl_label = 'Reset Normals'

    def execute(self, context):
        mode = context.active_object.mode
        try:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_tools(mode='RESET')
        finally:
            bpy.ops.object.mode_set(mode=mode)
        return { 'FINISHED' }
    
