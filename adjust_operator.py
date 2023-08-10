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
from mathutils import Vector, Quaternion
import math

from . import selection

# There's one somewhat annoying limitation here, which is that it mostly assumes mostly simple quad modeling.
# That works ok for my use case, but it might be interesting to extend this to more complicated models.

class AdjustState:
    """Stores and answers questions about the state of the mesh for the adjustment."""
    def __init__(self, mesh, selected_edges):
        self.mesh = mesh
        self.affected_loops = set()
        self.affected_vertices = set()
        self.selected_edges = selected_edges
        for e in selected_edges:
            edge = self.mesh.edges[e]
            self.affected_vertices.add(edge.vertices[0])
            self.affected_vertices.add(edge.vertices[1])

    def set_loop_normal(self, loop, normal):
        loop.normal = normal
        self.affected_loops.add(loop.index)

    def should_affect_loop(self, loop):
        return loop.vertex_index in self.affected_vertices

    def get_connected_polygons(self, vertex_id):
        """Returns all MeshPolygon objects in this mesh that have vertex_id as a vertex"""
        connected = list()
        for p in self.mesh.polygons:
            if vertex_id in p.vertices:
                connected.append(p)
        return connected
    
    def get_influential_polygons(self, poly, loop):
        """Return all polygons that should influence the normal of a given loop.  This means they're connected to the same vertex and share a selected edge."""
        connected = [p for p in self.get_connected_polygons(loop.vertex_index) if p != poly]
        influential = [p for p in connected if self.shares_selected_edge(poly, p)]
        return influential

    def shares_selected_edge(self, poly_a, poly_b):
        """Returns True if two polygons share an edge that is in the selected edge set."""
        for e in self.get_shared_edges(poly_a, poly_b):
            if e in self.selected_edges:
                return True
        return False
    
    def get_shared_edges(self, poly_a, poly_b):
        """Gets a list of edge indices shared by two polygons"""
        a_edges = set([self.mesh.loops[l].edge_index for l in poly_a.loop_indices])
        return [self.mesh.loops[l].edge_index for l in poly_b.loop_indices if self.mesh.loops[l].edge_index in a_edges]
    
    def should_smooth(self, poly_a, poly_b):
        """Given two polygons, figure out if their shared edge should have its normals smoothed or split."""
        p1 = self.mesh.polygons[poly_a]
        p2 = self.mesh.polygons[poly_b]

        shared = self.get_shared_edges(p1, p2)
        if len(shared) == 0:
            return False
        
        # This might not work in some cases, so... those strange cases aren't supported.
        edge_id = shared[0]
        edge = self.mesh.edges[edge_id]

        if edge_id in self.selected_edges:
            return False
        if edge.use_edge_sharp:
            return False
        
        angle = p1.normal.angle(p2.normal)
        return angle < self.mesh.auto_smooth_angle

    def get_smooth_adjacent(self, candidates, poly_id):
        """Given a list of candidate polygons, return any that are adjacent to poly_id and should be smoothed."""
        ret = list()
        for p in candidates:
            if p == poly_id:
                continue
            if self.should_smooth(poly_id, p):
                ret.append(p)
        return ret
    
    
    def get_smooth_set(self, candidates, poly_id):
        """Given a list of candidate polygons, return a set of polygons that should have its normals smoothed with that poly_id"""
        smooth = set([poly_id])
        remaining = list([poly_id])
        while len(remaining) > 0:
            p = remaining.pop()
            new = self.get_smooth_adjacent(candidates, p)
            for n in new:
                if n not in smooth:
                    remaining.append(n)
                    smooth.add(n)

        return smooth
    

def get_mesh(context):
    obj = context.active_object
    mesh = obj.data
    mesh.calc_normals_split()
    return mesh

def get_seams(mesh):
    return [e for e in mesh.edges if e.use_seam]

def get_edge_set(edges):
    return set([e.index for e in edges])

def adjust_loop(state, this_poly, loop):
    """Adjust the split normal of a given loop."""
    normals = list()
    rotations = list()

    # Only adjust loops associated with affected vertices
    if not state.should_affect_loop(loop):
        return

    # Start with the existing normal
    new_normal = Vector(loop.normal)

    # For each influential polygon, rotate the normal so that the resulting
    # angle will be 90deg.
    for that_poly in state.get_influential_polygons(this_poly, loop):
        # Get the total angle between the polygons
        angle = this_poly.normal.angle(that_poly.normal)
        # We want a 90 degree difference between them
        angle -= (math.pi / 2)
        # ... and this loop should rotate to cover half the delta 
        angle /= 2

        axis = this_poly.normal.cross(that_poly.normal).normalized() 
        #axis = loop.normal.cross(that_poly.normal).normalized() 
        new_normal.rotate(Quaternion(axis, angle))

    state.set_loop_normal(loop, new_normal)

def smooth_normals(state):
    """Average out normals for loops that should be smooth shaded"""

    # The previous steps may have left split normals across edges that should be smooth shaded.
    # This smooths them back out.

    for vertex_id in state.affected_vertices:
        connected = [p.index for p in state.get_connected_polygons(vertex_id)]

        seen = set()
        for poly in connected:
            if poly in seen:
                continue
            smooth_set = state.get_smooth_set(connected, poly)

            loops = list()
            for poly in smooth_set:
                seen.add(poly)
                for l in state.mesh.polygons[poly].loop_indices:
                    loop = state.mesh.loops[l]
                    if loop.vertex_index == vertex_id:        
                        loops.append(state.mesh.loops[l])

            averaged = Vector()
            for loop in loops:
                averaged += loop.normal
            averaged /= len(loop.normal)
            for loop in loops:
                state.set_loop_normal(loop, averaged)


class TrimNormalsAdjustOperator(bpy.types.Operator):
    bl_idname = 'opr.trim_normals_adjust_operator'
    bl_label = 'Adjust Trim Normals'

    def execute(self, context):
        mode = context.active_object.mode
        try:
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
            bpy.ops.object.mode_set(mode='OBJECT')

            mesh = get_mesh(context);
            mesh.use_auto_smooth = True

            state = AdjustState(mesh, get_edge_set([e for e in mesh.edges if e.select]))

            for p in mesh.polygons:
                for l in p.loop_indices:
                    adjust_loop(state, p, state.mesh.loops[l])

            smooth_normals(state)

            normal_set = [l.normal if l.index in state.affected_loops else Vector() for l in mesh.loops]
            mesh.normals_split_custom_set(normal_set)
        finally:
            bpy.ops.object.mode_set(mode=mode)

        return { 'FINISHED' }
    

    