import bpy
import mathutils
import bmesh
import numpy as np
import json
import math
from mathutils import Vector

# Other existing functions...

def save_initial_object(obj):
    # Create a dictionary to store object's data
    initial_data = {
        'name': obj.name,
        'mesh_data': obj.data.copy(),
        'location': obj.location.copy(),
        'rotation_euler': obj.rotation_euler.copy(),
        'scale': obj.scale.copy(),
    }
    return initial_data

def create_copy_away_from_initial(initial_data, offset=(1, 0, 0)):
    # Add the initial object's mesh data to the scene
    new_mesh = initial_data['mesh_data']
    new_obj = bpy.data.objects.new(initial_data['name'] + "_copy", new_mesh)
    bpy.context.collection.objects.link(new_obj)
    
    # Restore location, rotation, and scale
    new_obj.location = initial_data['location'] + offset
    new_obj.rotation_euler = initial_data['rotation_euler']
    new_obj.scale = initial_data['scale']
    
    return new_obj

def is_2d_shape(obj):
    return len(obj.data.polygons) == 1  # Assuming a shape with 1 face is 2D

def perform_slicing(A, stitch_height):
    if A:
        print('Object selected')
        
        local_bbox_corners = [mathutils.Vector(corner) for corner in A.bound_box]
        
        # Transform the bounding box corners to world space
        world_bbox_corners = [A.matrix_world @ corner for corner in local_bbox_corners]
        
        # Create a new mesh for the bounding box
        mesh = bpy.data.meshes.new("BoundingBox")
        bbox_object = bpy.data.objects.new("BoundingBox", mesh)
        bpy.context.collection.objects.link(bbox_object)
        
        # Define the vertices of the bounding box
        vertices = [corner for corner in world_bbox_corners]
        
        # Define the edges of the bounding box
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Bottom face
            (4, 5), (5, 6), (6, 7), (7, 4),  # Top face
            (0, 4), (1, 5), (2, 6), (3, 7)   # Side edges
        ]
        
        # Create the mesh
        mesh.from_pydata(vertices, edges, [])
        mesh.update()
        
        # Get the bounding box dimensions
        bbox = [A.matrix_world @ mathutils.Vector(corner) for corner in A.bound_box]
        
        # Calculate the minimum and maximum Z values in the object’s local space
        min_z = min([v.z for v in bbox])
        max_z = max([v.z for v in bbox])
        
        # Calculate the dimensions of the bounding box
        min_x = min([v.x for v in bbox])
        max_x = max([v.x for v in bbox])
        min_y = min([v.y for v in bbox])
        max_y = max([v.y for v in bbox])
        
        bbox_width = max_x - min_x
        bbox_depth = max_y - min_y
        bbox_height = max_z - min_z
        
        # Add a little extra to the dimensions
        extra = 5 
        plane_width = bbox_width + extra
        plane_depth = bbox_depth + extra
        
        # Define the number of planes to add
        print('float division',bbox_height / stitch_height)
        print('int division',bbox_height // stitch_height)
        print('bbox height', bbox_height)
        
        num_planes = int(bbox_height // stitch_height) # You can adjust this number as needed

        # Calculate the distance between each plane
        step = (max_z - min_z) / (num_planes - 1)
        
        # Add planes at equidistant positions along the Z axis
        planes = []
        for i in range(num_planes):
            z_pos = (min_z + i * step) 
           
            plane_loc = A.matrix_world @ mathutils.Vector((0, 0, z_pos))
            bpy.ops.mesh.primitive_plane_add(location=plane_loc)
            
            # Get the newly created plane
            plane = bpy.context.object
            plane.rotation_euler = A.rotation_euler
            
            # Scale the plane to cover the bounding box dimensions plus extra
            plane.scale = (plane_width , plane_depth , 1)
            
            planes.append(plane)
            
        j = 0
        for idx, plane in enumerate(planes):
            bpy.ops.object.select_all(action='DESELECT')
            A.select_set(True)
            bpy.context.view_layer.objects.active = A
            bpy.ops.object.duplicate()
            intersected_object = bpy.context.object
            j += 1
            letter = chr(96 + j) 
            intersected_object.name = f"slice_{letter}"
            
            mod = intersected_object.modifiers.new(name=f"Boolean_Intersect_{idx}", type='BOOLEAN')
            mod.operation = 'INTERSECT'
            mod.object = plane
            
            # Apply the modifier
            bpy.context.view_layer.objects.active = intersected_object
            bpy.ops.object.modifier_apply(modifier=mod.name)
            
            print(intersected_object.name, 'is 2D:', is_2d_shape(intersected_object))
            
            if not is_2d_shape(intersected_object):
                print('removing')
                j -= 1
                bpy.data.objects.remove(intersected_object, do_unlink=True)
            
            bpy.data.objects.remove(plane, do_unlink=True)
        
        bpy.data.objects.remove(A, do_unlink=True)

    else:
        print('Please select an object!')

def make_copy(current_obj, x):
    initial_mesh_data = save_initial_object(current_obj)
    copy_offset = mathutils.Vector((x, 0, 0)) 
    create_copy_away_from_initial(initial_mesh_data, offset=copy_offset)

def set_shape_vertices(obj, new_vertices):
    for i, vert in enumerate(obj.data.vertices):
        vert.co.xy = new_vertices[i]

def extract_vertices_from_object(obj):
    if obj.type == 'MESH':
        return [v.co for v in obj.data.vertices]
    return []

def get_boundary_vertices(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    
    boundary_verts = []
    for edge in bm.edges:
        if edge.is_boundary:
            boundary_verts.append(edge.verts[0].co)
            boundary_verts.append(edge.verts[1].co)
    
    bm.free()
    
    # Remove duplicates while preserving order
    unique_boundary_verts = []
    [unique_boundary_verts.append(v) for v in boundary_verts if v not in unique_boundary_verts]
    
    return unique_boundary_verts

def calculate_perimeter_and_distances(ordered_verts):
    distances = [0.0]
    L = 0.0
    for i in range(len(ordered_verts) - 1):
        dist = (ordered_verts[i+1] - ordered_verts[i]).length
        L += dist
        distances.append(L)
    L += (ordered_verts[0] - ordered_verts[-1]).length  # Closing the loop
    distances.append(L)
    return L, distances

def resample_vertices(original_vertices, w):
    original_vertices = [Vector(v) for v in original_vertices]
    # Calculate perimeter and cumulative distances
    L, distances = calculate_perimeter_and_distances(original_vertices)
    
    # Number of resampled vertices
    m = int(L / w)
    
    # Parameter t values for resampling
    t_values = [i / m for i in range(m)]
    
    # Resample vertices based on t values
    new_verts = []
    for t in t_values:
        target_length = t * L
        for i in range(len(distances) - 1):
            if distances[i] <= target_length < distances[i+1]:
                segment_length = distances[i+1] - distances[i]
                segment_t = (target_length - distances[i]) / segment_length
                if i < len(original_vertices) - 1:
                    new_vert = original_vertices[i].lerp(original_vertices[i+1], segment_t)
                    new_verts.append(new_vert)
                break
    
    return new_verts


def calculate_geometric_center(vertices):
    center = Vector((0.0, 0.0, 0.0))
    for v in vertices:
        center += v
    center /= len(vertices)
    return center

def sort_vertices_by_angle(vertices):
    center = calculate_geometric_center(vertices)
    sorted_vertices = sorted(vertices, key=lambda v: math.atan2(v.y - center.y, v.x - center.x))
    return sorted_vertices

####

def main():
    current_obj = bpy.context.object
    
    # Making a copy of the initial mesh
    make_copy(current_obj, 60)
    
    # Perform slicing
    stitch_height = 0.25  # Change depending on yarn type 
    perform_slicing(current_obj, stitch_height)
    
    sliced_objects = []
    for obj in bpy.data.objects:
        if obj.name.startswith('slice'):
            make_copy(obj, 30)
            sliced_objects.append(obj)

    slice_vertices = {}
    stitch_width = 0.2  # Example distance for resampling

    for slice_obj in sliced_objects:
        vertices = []
        for vert in slice_obj.data.vertices:
            co = slice_obj.matrix_world @ vert.co
            vertices.append(co)
        
        # Sort vertices based on their angle around the geometric center
        sorted_vertices = sort_vertices_by_angle(vertices)
        
        # Resample vertices based on the desired distance
        resampled_vertices = resample_vertices(sorted_vertices, stitch_width)
        
        # Convert to list of tuples for JSON serialization
        slice_vertices[slice_obj.name] = [tuple(v) for v in resampled_vertices]
    
    file_path = r"Z:\Blender Foundation\My Files\worm.json"
   
    with open(file_path, 'w') as file:
        json.dump(slice_vertices, file, indent=4)


main()
