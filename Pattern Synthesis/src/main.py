import json
import numpy as np
import os
import open3d as o3d # type: ignore
from utils import interpolate_colors, visualizer, visualize_animation, generate_row_pattern
from dp import dist_matrix, compute_bulges_indents, dp_solution_with_shape_info
from dfs import dfs_traversal, build_graph
from write_pattern import reform_crochet_pattern
import matplotlib.pyplot as plt
from time import time


def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


def get_segments(folder_path):
    segments = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.json'):
            print(f"Reading.......{file_name}")
            file_path = os.path.join(folder_path, file_name)
            json_data = load_json(file_path)
            segments.append((file_name, json_data))
    return segments


def get_crochet_pattern(data, color_start, color_end):
    """
    Generates crochet patterns and connection data for visualization, returning the complete pattern.
    """

    cro_pattern = ''
    # Extract vertices and store them in a list
    slice_names = list(data.keys())
    all_vertices = [np.array(data[slice_name]).T for slice_name in slice_names]
    
    stitch_width = 0.15
    W = stitch_width

    num_rows = len(all_vertices) - 1
    
    colors = interpolate_colors(color_start, color_end, num_rows)

    patterns_data = []  # Store all necessary data for visualization

    # Generate crochet patterns row by row
    for loop in range(num_rows):
        points_1 = all_vertices[loop]
        points_2 = all_vertices[loop + 1]

        n = points_1.shape[1]
        m = points_2.shape[1]

        #### TODO #################
        if m > 2*m or m>2*n:
            # Insert a new row
            pass 
        ###########################

        dist = dist_matrix(points_1, points_2)
        is_bulge, is_indent = compute_bulges_indents(points_1, points_2)
        dp,path = dp_solution_with_shape_info(n, m, dist, W, is_bulge, is_indent)
        #print(f'Row {loop + 1}: (going from: {n} to {m})')
        connections = path[(n, m)]
       
        row_p, indices = generate_row_pattern(points_1, points_2, connections)
        p = reform_crochet_pattern(row_p)
        #print(p)
        # Store row data for later visualization
        row_data = {
            'points_1': points_1,
            'points_2': points_2,
            'indices':indices,
            'color': colors[loop]
        }
        patterns_data.append(row_data)

        cro_pattern += f'Row {loop + 1}: {p}  ({m})\n'

    return cro_pattern, patterns_data


def visualizer(ax, patterns_data):
    """
    Visualizes the crochet patterns for all rows sequentially.
    """
    for row_data in patterns_data:
        points_1 = row_data['points_1']
        points_2 = row_data['points_2']
        indices = row_data['indices']
        color = row_data['color']
        visualize_animation(ax, points_1, points_2,indices, color)
        

def get_last_row(segment_name, segmented_parts):
  
    # Search for the segment_name in segmented_parts
    for name, data in segmented_parts:
        if name == segment_name:
            slices = sorted(data.keys())  # Sort slice keys (e.g., slice_a, slice_b, etc.)
            if slices:
                last_slice = slices[-1]  # Get the last slice
                return data[last_slice]   # Return the points associated with the last slice
            else:
                return [] 
    return []  

def get_first_row(segment_name, segmented_parts):
  
    # Search for the segment_name in segmented_parts
    for name, data in segmented_parts:
        if name == segment_name:
            slices = sorted(data.keys())  # Sort slice keys (e.g., slice_a, slice_b, etc.)
            if slices:
                first_slice = slices[0]  # Get the last slice
                return data[first_slice]   # Return the points associated with the last slice
            else:
                return [] 
    return []  

def add_last_row(segment_name, new_row, segmented_parts):
    # Create a lookup dictionary for quick access
    segmented_dict = dict(segmented_parts)
    
    if segment_name in segmented_dict:
        data = segmented_dict[segment_name]
        
        # Determine the new slice key
        if data:
            slices = sorted(data.keys())  # Sort slice keys
            if slices:
                last_slice = slices[-1]  # Get the last slice
                # Derive the new slice key (assuming sequential naming like slice_a, slice_b)
                next_index = len(slices)  # Next index in sequence
                new_slice_key = f"slice_{chr(ord('a') + next_index)}"  # Generate new slice key (e.g., slice_d)
            else:
                new_slice_key = "slice_a"  # If no slices exist, start with slice_a
        
        else:
            new_slice_key = "slice_a"  # Start with slice_a if data is empty
        
        # Add the new row to the data
        data[new_slice_key] = new_row
        
        # Update the segmented_parts with the modified segment
        segmented_parts[:] = [(name, data) if name == segment_name else (name, data) for name, data in segmented_parts]
    else:
        print(f"Segment {segment_name} not found in segmented_parts.")


def add_first_row(new_row, data):
    # Generate a new dictionary with shifted keys
    new_data = {}

    # Add the new row as the first slice
    new_data['slice_a'] = new_row
    
    # Shift existing keys down by one (e.g., 'slice_a' -> 'slice_b', 'slice_b' -> 'slice_c', etc.)
    for i, (key, value) in enumerate(sorted(data.items()), 1):
        new_key = f"slice_{chr(ord('a') + i)}"  # Shift the slice key
        new_data[new_key] = value

    return new_data



def main():

    t1 = time()
    ######## SEGMENTS ###########
    folder_path = 'Z:\Blender Foundation\My Files\\pot'
    #folder_path = 'Z:\Blender Foundation\My Files\\worm'
    #folder_path = 'Z:\Blender Foundation\My Files\\pig'
    #folder_path = 'Z:\Blender Foundation\My Files\\cactus'

    #folder_path = 'Z:\Blender Foundation\My Files\\teddy'
    #metadata = load_json(folder_path+'/metadata.json')

    metadata = {
    'teddy_b.json': [('teddy_left_l.json', 0), ('teddy_t', 1), ('teddy_arm_l', 1), ('teddy_arm_r', 1), ('teddy_right_l.json',0)],
    'teddy_h.json':[('teddy_b.json', 0),('ear1.json',1), ('ear2.json',1)],  # 0 = sew-on, 1 = attach separately
    }

    metadata = {
    'cactus_main.json': [('cactus_left.json', 1), ('cactus_right.json',1)],
    }


    segmented_parts = get_segments(folder_path)

    # Set up the plot for visualization
    fig = plt.figure()
    plt.axis('off')

    ax = fig.add_subplot(111, projection='3d')
    ax.grid(False)


    #completed_segments = {name for name, _ in segmented_parts}
    completed_segments = set()

    with open('none.txt', 'w') as file:
        for segment_name, data in segmented_parts:

            if segment_name not in completed_segments:
                print("\n\nCURRENT SEGMENT: ", segment_name)
                print()

                color_start = np.array([0.5, 0, 0.5])  # Dark purple
                color_end = np.array([1, 0.5, 1])  # Light purple

                last_rows_connections = []
                n_sew_ons = 0

                if segment_name in metadata:
                    
                    connected_components = metadata.get(segment_name)
                    # Get a list of connections with 0
                    sew_ons = [entry for entry in connected_components if entry[1] == 0]
                    n_sew_ons = len(sew_ons)

                    for seg,_ in sew_ons:
                        
                        seg_data  = next((d for s, d in segmented_parts if s == seg), None)

                        last_row = get_last_row(seg, segmented_parts)
                        new_row = [[x, y, z + 0.2] for x, y, z in last_row]

                        add_last_row(seg, new_row, segmented_parts)

                        if seg not in completed_segments:
                            print(f"processing {seg}")
                            file.write(f'\n{seg}\n')
                            cro_pattern, patterns_data = get_crochet_pattern(seg_data, color_start, color_end)
                            print(cro_pattern)
                            file.write(cro_pattern)
                            # Visualize the generated patterns for the current segment
                            visualizer(ax, patterns_data)
                            completed_segments.add(seg)

                        last_rows_connections.append(new_row)

                        
                        
                print(f"processing {segment_name}")
                completed_segments.add(segment_name)
                file.write(f'\n{segment_name}\n')

                if last_rows_connections:
                    last_rows_connections = [point for sublist in last_rows_connections for point in sublist]
                    data['slice_a'] = last_rows_connections
                    s = f"NOTE: For this segment, sew-on across all {n_sew_ons} components ({', '.join(s for s, _ in sew_ons)}) to attach.....\n"
                    print(s)
                    file.write(s)

                ################# GET PATTERN FOR SEGMENT #########################
                # Generate crochet patterns and data needed for visualization
                cro_pattern, patterns_data = get_crochet_pattern(data, color_start, color_end)
                print(cro_pattern)
                file.write(cro_pattern)
                # Visualize the generated patterns for the current segment
                #visualizer(ax, patterns_data)
                ###################################################################
                
    # Display the visualization for the current segment
    #plt.show()
    # Close the plot to avoid overlap in subsequent iterations
    #plt.close(fig)

    t2 = time()
    print('Elapsed time is %f seconds.' % (t2-t1))


       

if __name__ == '__main__':
    main()
