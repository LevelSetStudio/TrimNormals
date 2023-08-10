# Copyright (c) 2023 Level Set Studio LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import bpy
import bmesh

def get_save_collection(mesh):
    attr = mesh.attributes.get('trimsheet_edge')
    if not attr:
        attr = mesh.attributes.new('trimsheet_edge', 'BOOLEAN', 'EDGE')
    return attr

def get_saved_edges(context):
    mode = context.active_object.mode
    marked = set()
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
        attr = get_save_collection(context.active_object.data)
        for i in range(len(attr.data)):
            if getattr(attr.data[i], "value"):
                marked.add(i)
    finally:
        bpy.ops.object.mode_set(mode=mode)
    return marked
        
class TrimNormalsSelectSeamsOperator(bpy.types.Operator):
    bl_idname = 'opr.trim_normals_select_seams'
    bl_label = 'Select Seams'
    
    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        for e in context.active_object.data.edges:
            e.select = e.use_seam

        bpy.ops.object.mode_set(mode='EDIT')
        return { 'FINISHED' }
    
class TrimNormalsSelectSharpOperator(bpy.types.Operator):
    bl_idname = 'opr.trim_normals_select_sharp'
    bl_label = 'Select Sharp'
    
    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        for e in context.active_object.data.edges:
            e.select = e.use_edge_sharp

        bpy.ops.object.mode_set(mode='EDIT')
        return { 'FINISHED' }

class TrimNormalsSaveSelectedOperator(bpy.types.Operator):
    bl_idname = 'opr.trim_normals_save_selected'
    bl_label = 'Save Selection'

    def execute(self, context):
        mesh = context.active_object.data

        mode = context.active_object.mode
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
            attr = get_save_collection(mesh)
            attr.data.foreach_set("value", [e.select for e in mesh.edges])
        finally:
            bpy.ops.object.mode_set(mode=mode)
        return { 'FINISHED' }

class TrimNormalsRestoreSavedOperator(bpy.types.Operator):
    bl_idname = 'opr.trim_normals_restore_saved'
    bl_label = 'Restore Saved Selection'

    def execute(self, context): 
        saved_edges = get_saved_edges(context)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')

        bm = bmesh.from_edit_mesh(context.active_object.data)
        for e in bm.edges:
            e.select_set(e.index in saved_edges)
        return { 'FINISHED' }

