import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import open3d as o3d # type: ignore


def visualizer(all_vertices):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # Iterate over each cell in the list of vertices
    for points in all_vertices:
        x = points[0, :]
        y = points[1, :]
        z = points[2, :]
        
        # Plot the vertices and connect the last point to the first
        ax.plot(x.tolist() + [x[0]], y.tolist() + [y[0]], z.tolist() + [z[0]], 'bo-', linewidth=2)
    
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_zlabel('Z-axis')
    ax.set_title('3D Shape Visualizer (rows)')
    
    #plt.grid(True)
    plt.show()

def show_plot():
    plt.show()


def interpolate_colors(color_start, color_end, num_colors):
    color_start = np.array(color_start)
    color_end = np.array(color_end)
    colors = np.zeros((num_colors, 3))

    for i in range(num_colors):
        t = i / (num_colors - 1)
        colors[i, :] = (1 - t) * color_start + t * color_end

    return colors



def parse_connection(connection):
    """
    Parses a connection string into indices for two sets of points.
    
    Args:
    connection (str): The connection string in the format 'aX -> bY,Z,...'.
    
    Returns:
    tuple: Two lists of indices.
    """
    # Split the connection string into parts
    parts = connection.split('->')
    a_part = parts[0].strip()
    b_part = parts[1].strip()

    # Parse a_part: remove 'a' and split by commas
    a_indices = list(map(int, a_part.replace('a', '').split(',')))
    
    # Parse b_part: remove 'b' and split by commas
    b_indices = [int(x.replace('b', '')) for x in b_part.split(',')]
    
    return a_indices, b_indices


def generate_row_pattern(points1, points2, connections):
    """
    Parses the connections between two sets of 3D points and generates a row pattern string.

    Parameters:
    points1 (np.ndarray): The first set of points (shape: (3, n)).
    points2 (np.ndarray): The second set of points (shape: (3, m)).
    connections (list): List of connection strings.

    Returns:
    str: A string describing the row pattern.
    """
    row_pattern = ''
    indices = []

    for connection in connections:
        a_indices, b_indices = parse_connection(connection)
        points_a = points1[:, a_indices]
        points_b = points2[:, b_indices]

        if points_a.shape[1] == 1 and points_b.shape[1] == 1:
            # Single connection
            stitch_type = 'sc,'  # Single crochet
        elif points_a.shape[1] == 1 and points_b.shape[1] > 1:
            # Increase connection
            stitch_type = 'inc,'  # Increase
        elif points_a.shape[1] > 1 and points_b.shape[1] == 1:
            # Decrease connection
            stitch_type = 'dec,'  # Decrease
        else:
            raise ValueError('Invalid connection format.')

        row_pattern += stitch_type
        indices.append((stitch_type, a_indices, b_indices))

    return row_pattern, indices


def visualize_animation(ax, points1, points2, row_pattern, row_color):
    """
    Visualizes the animation of connections between two sets of 3D points, and ensures the rows are closed.
    Returns the row pattern string describing the connections.

    Parameters:
    ax (matplotlib.axes._subplots.Axes3DSubplot): The 3D axis to plot on.
    points1 (np.ndarray): The first set of points (shape: (3, n)).
    points2 (np.ndarray): The second set of points (shape: (3, m)).
    connections (list): List of connection strings.
    row_color (tuple): RGB color for the connections.

    Returns:
    str: A string describing the row pattern.
    """
   
    # Plot the original points
    ax.plot3D(points1[0, :], points1[1, :], points1[2, :], 'o-', color=row_color, linewidth=2)
    ax.plot3D(points2[0, :], points2[1, :], points2[2, :], 'o-', color=row_color, linewidth=2)
    
    # Ensure rows are closed
    ax.plot3D([points1[0, -1], points1[0, 0]], [points1[1, -1], points1[1, 0]], [points1[2, -1], points1[2, 0]], 'o-', color=row_color, linewidth=2)
    ax.plot3D([points2[0, -1], points2[0, 0]], [points2[1, -1], points2[1, 0]], [points2[2, -1], points2[2, 0]], 'o-', color=row_color, linewidth=2)
    

    # Iterate through each connection string
    for stitch_type, a_indices, b_indices in row_pattern:
        points_a = points1[:, a_indices]
        points_b = points2[:, b_indices]

        if stitch_type == 'sc,':
            # Single connection
            color = 'k'
            X = [points_a[0, 0], points_b[0, 0]]
            Y = [points_a[1, 0], points_b[1, 0]]
            Z = [points_a[2, 0], points_b[2, 0]]
            ax.plot3D(X, Y, Z, color=color, linewidth=2)

        elif stitch_type == 'inc,':
            # Increase connection
            color = 'r'
            for j in range(points_b.shape[1]):
                X = [points_a[0, 0], points_b[0, j]]
                Y = [points_a[1, 0], points_b[1, j]]
                Z = [points_a[2, 0], points_b[2, j]]
                ax.plot3D(X, Y, Z, color=color, linewidth=2)

        elif stitch_type == 'dec,':
            # Decrease connection
            color = 'g'
            for i in range(points_a.shape[1]):
                X = [points_a[0, i], points_b[0, 0]]
                Y = [points_a[1, i], points_b[1, 0]]
                Z = [points_a[2, i], points_b[2, 0]]
                ax.plot3D(X, Y, Z, color=color, linewidth=2)

        else:
            raise ValueError('Invalid connection format.')
        

    # Update axis settings
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Connections')
    plt.draw()
    plt.pause(0.2)  # Adjust this for animation speed

    


def reconstruct_mesh(all_vertices, all_connections):
    """
    Reconstructs a 3D mesh using all_vertices and the provided connections.

    Parameters:
    - all_vertices: List of numpy arrays where each array represents the vertices of a slice.
    - all_connections: List of strings, each representing a connection between vertices.

    Returns:
    - mesh: An open3d.geometry.LineSet object representing the mesh.
    """
    # Combine all vertices into a single list for easier indexing
    vertices = np.hstack(all_vertices).T  # (n, 3)

    # Initialize lists to store line vertices and their connections
    lines = []

    # Track the cumulative count of vertices per row to adjust indices
    cumulative_vertex_count = np.cumsum([0] + [v.shape[1] for v in all_vertices[:-1]])

    # Process each connection to create lines
    for connection in all_connections:
        a_indices, b_indices = parse_connection(connection)

        # Adjust indices for the cumulative vertex count
        a_indices = [idx + cumulative_vertex_count[i] for i, idx in enumerate(a_indices)]
        b_indices = [idx + cumulative_vertex_count[i + 1] for i, idx in enumerate(b_indices)]

        # Add the connections to the lines list
        for a, b in zip(a_indices, b_indices):
            lines.append([a, b])

    # Create an Open3D LineSet object
    mesh = o3d.geometry.LineSet()
    mesh.points = o3d.utility.Vector3dVector(vertices)
    mesh.lines = o3d.utility.Vector2iVector(lines)

    return mesh