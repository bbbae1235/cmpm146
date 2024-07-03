import queue, math

def find_path(source_point, destination_point, mesh):
    """
    Searches for a path from source_point to destination_point through the mesh.

    Args:
        source_point: starting point of the pathfinder
        destination_point: the ultimate goal the pathfinder must reach
        mesh: pathway constraints the path adheres to

    Returns:
        A path (list of points) from source_point to destination_point if exists
        A list of boxes explored by the algorithm
    """
    # Initialize variables
    mesh_boxes = mesh['boxes']
    adj_boxes = mesh['adj']
    source_box = find_box(source_point, mesh_boxes)
    destination_box = find_box(destination_point, mesh_boxes)

    if source_box is None or destination_box is None:
        print("Source or destination is not inside any box.")
        return [], set()

    # Create PQ for source and destination    
    frontier = queue.PriorityQueue()
    frontier.put((0, source_box, 'destination', source_point))
    frontier.put((0, destination_box, 'source', destination_point))

    # Tracking Forward Search
    came_from_forward = {source_point: None}  # keep track of forward visited points
    cost_so_far_forward = {source_point: 0}  # keep track of forward costs
    boxes_forward = {source_box}  # keep track of forward visited boxes 

    # Tracking Backward Search
    came_from_backward = {destination_point: None}  # keep track of backward visited points
    cost_so_far_backward = {destination_point: 0}  # keep track of backward costs
    boxes_backward = {destination_box}  # keep track of backward visited boxes 

    # Reconstruct path when searches meet
    def reconstruct_path(meeting_point):
        path_forward = []
        current = meeting_point
        while current is not None:
            path_forward.append(current)
            current = came_from_forward.get(current)
        path_forward.reverse()

        path_backward = []
        current = came_from_backward.get(meeting_point)
        while current is not None:
            path_backward.append(current)
            current = came_from_backward.get(current)

        return path_forward + path_backward, boxes_forward.union(boxes_backward)

    # Perform the bidirectional search
    while not frontier.empty():
        # Forward search
        priority, current_box, goal, current_point = frontier.get()
        if goal == 'destination':
            # Forward frontier
            boxes_forward.add(current_box)
            if current_point in came_from_backward:
                return reconstruct_path(current_point)

            for neighbor in adj_boxes.get(current_box, []):
                if neighbor not in boxes_forward:
                    # Determines where to enter on neighbor box
                    neighbor_point = entry_point(current_point, neighbor)
                    new_cost = cost_so_far_forward[current_point] + euclidean_distance(current_point, neighbor_point)
                    if neighbor_point not in cost_so_far_forward or new_cost < cost_so_far_forward[neighbor_point]:
                        cost_so_far_forward[neighbor_point] = new_cost
                        priority = new_cost + heuristic(neighbor_point, destination_point)  # Add heuristics to the cost
                        frontier.put((priority, neighbor, goal, neighbor_point))
                        boxes_forward.add(neighbor)
                        came_from_forward[neighbor_point] = current_point
        elif goal == 'source':
            # Backward frontier
            boxes_backward.add(current_box)
            if current_point in came_from_forward:
                return reconstruct_path(current_point)

            for neighbor in adj_boxes.get(current_box, []):
                if neighbor not in boxes_backward:
                    # Determines where to enter on neighbor box
                    neighbor_point = entry_point(current_point, neighbor)
                    new_cost = cost_so_far_backward[current_point] + euclidean_distance(current_point, neighbor_point)
                    if neighbor_point not in cost_so_far_backward or new_cost < cost_so_far_backward[neighbor_point]:
                        cost_so_far_backward[neighbor_point] = new_cost
                        priority = new_cost + heuristic(neighbor_point, source_point)  # Add heuristics to the cost
                        frontier.put((priority, neighbor, goal, neighbor_point))
                        boxes_backward.add(neighbor)
                        came_from_backward[neighbor_point] = current_point

    print("No path found.")
    return [], boxes_forward.union(boxes_backward)

# Returns source and destination box
def find_box(point, boxes):
    x, y = point
    for box in boxes:
        x1, x2, y1, y2 = box
        if x1 <= x <= x2 and y1 <= y <= y2:
            return box
    return None

# Find entry point in each box
def entry_point(point, box):
    x, y = point
    x1, x2, y1, y2 = box
    constrained_x = max(x1, min(x2, x))
    constrained_y = max(y1, min(y2, y))
    return (constrained_x, constrained_y)

# Calculate distance between points
def euclidean_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Get cost from current point to destination
def heuristic(point, goal):
    return euclidean_distance(point, goal)
