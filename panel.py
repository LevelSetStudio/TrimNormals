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

class TrimNormalsPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Trim Normals'
    bl_label = 'Trim Normals'

    def draw(self, context):
        col = self.layout.column()

        col.label(text='Selection')
        col.operator('opr.trim_normals_select_seams')
        col.operator('opr.trim_normals_select_sharp')
        col.separator()
        col.operator('opr.trim_normals_save_selected')
        col.operator('opr.trim_normals_restore_saved')

        col.label(text='Modify Mesh')
        col.operator('mesh.customdata_custom_splitnormals_clear', text="Clear Custom Split Normals")

        adjust = col.row()
        adjust.scale_y = 2.0
        adjust.operator('opr.trim_normals_adjust_operator')
        pass


def register():
    pass
