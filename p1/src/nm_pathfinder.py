import queue, math

def find_path (source_point, destination_point, mesh):

    """
    Searches for a path from source_point to destination_point through the mesh

    Args:
        source_point: starting point of the pathfinder
        destination_point: the ultimate goal the pathfinder must reach
        mesh: pathway constraints the path adheres to

    Returns:

        A path (list of points) from source_point to destination_point if exists
        A list of boxes explored by the algorithm
    """

    mesh_boxes = mesh['boxes']
    adj_boxes = mesh['adj']
    source_box = find_box(source_point, mesh_boxes)
    destination_box = find_box(destination_point, mesh_boxes)
    frontier = queue.Queue()
    frontier.put((source_box, source_point))

    came_from = {source_point: None} #keep track of visited points
    cost_so_far = {source_point: 0} #keep track of costs
    boxes = {source_box} #keep track of visited boxes

    while not frontier.empty():
        current_box, current_point = frontier.get()
        boxes.add(current_box)
        if current_box == destination_box:
            path = [destination_point] #connects path to goal point
            while current_point is not None:
                path.append(current_point)
                current_point = came_from[current_point]
            path.reverse()
            return path, boxes
        else:
            for neighbor in adj_boxes.get(current_box):
                if neighbor not in boxes:
                    # determines where to enter on neighbor box
                    neighbor_point = entry_point(current_point, neighbor)
                    new_cost = cost_so_far[current_point] + euclidean_distance(current_point, neighbor_point)
                    if neighbor_point not in cost_so_far or new_cost < cost_so_far[neighbor_point]:
                        cost_so_far[neighbor_point] = new_cost
                        frontier.put((neighbor, neighbor_point))
                        boxes.add(neighbor)
                        came_from[neighbor_point] = current_point

    return None

# returns source and destination box
def find_box (point, boxes):
    x,y = point
    for box in boxes:
        x1, x2, y1, y2 = box
        if x1 <= x <= x2 and y1 <= y <= y2:
            return box
    return None

# find entry point in each box
def entry_point(point, box):
    x, y = point
    x1, x2, y1, y2 = box
    constrained_x = max(x1, min(x2, x))
    constrained_y = max(y1, min(y2, y))
    return (constrained_x, constrained_y)

#calculate distance between points
def euclidean_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
