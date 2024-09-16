import numpy as np

def dist_matrix(xyz_1, xyz_2):
    """
    Compute the Euclidean distance matrix between two sets of points using broadcasting.

    Parameters:
    xyz_1 (np.ndarray): An array of shape (3, n) containing the first set of points.
    xyz_2 (np.ndarray): An array of shape (3, m) containing the second set of points.

    Returns:
    np.ndarray: A distance matrix of shape (n, m) where each element (i, j) is the distance
                between point i in xyz_1 and point j in xyz_2.
    """
    # Compute pairwise squared differences and then distances
    diff = np.expand_dims(xyz_1.T, 1) - np.expand_dims(xyz_2.T, 0)
    dist = np.sqrt(np.sum(diff ** 2, axis=2))

    return dist


def compute_bulges_indents(points_A, points_B):
    """
    Compute whether points in `points_A` are bulges or indents based on their distances
    to the centroid of `points_A` and their nearest neighbors in `points_B`.

    Parameters:
    points_A (np.ndarray): An array of shape (3, n) containing the first set of points.
    points_B (np.ndarray): An array of shape (3, m) containing the second set of points.

    Returns:
    tuple: Two boolean arrays indicating bulges and indents.
    """
    n = points_A.shape[1]
    
    centroid_A = np.mean(points_A, axis=1, keepdims=True)
    
    is_bulge = np.zeros(n, dtype=bool)
    is_indent = np.zeros(n, dtype=bool)
    
    ai_to_centroid = np.sqrt(np.sum((points_A - centroid_A) ** 2, axis=0))
    
    ai_to_B = dist_matrix(points_A, points_B)
    
    # Find the indices of the 3 nearest neighbors in B for each point in A
    ai_nearest_indices_on_B = np.argsort(ai_to_B, axis=1)[:, :3]
    
    distances_to_centroid_B = np.zeros((n, 3))
    
    for i in range(n):
        for j in range(3):
            distances_to_centroid_B[i, j] = np.linalg.norm(points_B[:, ai_nearest_indices_on_B[i, j]] - centroid_A.flatten())
    
    # Determine bulges and indents
    is_bulge = np.all(distances_to_centroid_B > ai_to_centroid[:, np.newaxis], axis=1)
    is_indent = np.all(distances_to_centroid_B < ai_to_centroid[:, np.newaxis], axis=1)
    
    return is_bulge, is_indent




def dp_solution_with_shape_info(n, m, dist, W, is_bulge, is_indent):
    """
    Solve the dynamic programming problem with shape information for connecting points.

    Parameters:
    n (int): Number of points in set A.
    m (int): Number of points in set B.
    dist (np.ndarray): Distance matrix of shape (n, m).
    W (float): Weight for penalty calculations.
    is_bulge (np.ndarray): Boolean array indicating which points in A are bulges.
    is_indent (np.ndarray): Boolean array indicating which points in A are indents.

    Returns:
    tuple: A tuple containing:
        - dp (np.ndarray): The DP table of shape (n+1, m+1) with minimum costs.
        - path (dict): A dictionary containing paths for each (i, j) in the DP table.
    """
    # Initialize dp array with infinity
    dp = np.inf * np.ones((n + 1, m + 1))
    dp[0, 0] = 0

    # Initialize path dictionary to store connections
    path = {(i, j): [] for i in range(n + 1) for j in range(m + 1)}

    # Penalty factors
    alpha = 30  # Penalty for unnecessary increase
    beta = 30   # Penalty for unnecessary decrease

    # Fill the dp table
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            # Single connection
            cost = abs(dist[i - 1, j - 1] - W)
            if dp[i - 1, j - 1] + cost < dp[i, j]:
                dp[i, j] = dp[i - 1, j - 1] + cost
                path[(i, j)] = path.get((i - 1, j - 1), []) + [f'a{i - 1} -> b{j - 1}']

            # Increase connection
            if j >= 3:
                avg_dist = (dist[i - 1, j - 2] + dist[i - 1, j - 1]) / 2
                cost = abs(avg_dist - W)
                penalty = 0
                if not is_bulge[i - 1]:
                    penalty = alpha  # Penalize unnecessary increase
                if dp[i - 1, j - 2] + cost + penalty < dp[i, j]:
                    dp[i, j] = dp[i - 1, j - 2] + cost + penalty
                    path[(i, j)] = path.get((i - 1, j - 2), []) + [f'a{i - 1} -> b{j - 2}, b{j - 1}']

            # Decrease connection
            if i >= 3 and j >= 2:
                avg_dist = (dist[i - 2, j - 1] + dist[i - 1, j - 1]) / 2
                cost = abs(avg_dist - W)
                penalty = 0
                if not is_indent[i - 1]:
                    penalty = beta  # Penalize unnecessary decrease
                if dp[i - 2, j - 1] + cost + penalty < dp[i, j]:
                    dp[i, j] = dp[i - 2, j - 1] + cost + penalty
                    path[(i, j)] = path.get((i - 2, j - 1), []) + [f'a{i - 2}, a{i - 1} -> b{j - 1}']

    return dp, path
