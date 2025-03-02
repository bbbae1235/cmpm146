
from mcts_node import MCTSNode
from p2_t3 import Board
from random import choice
from math import sqrt, log

num_nodes = 1000
explore_faction = 2.

def traverse_nodes(node: MCTSNode, board: Board, state, bot_identity: int):
    """ Traverses the tree until the end criterion are met.
    e.g. find the best expandable node (node with untried action) if it exist,
    or else a terminal node

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 1 or 2

    Returns:
        node: A node from which the next stage of the search can proceed.
        state: The state associated with that node

    """
    best_child = None
    while not board.is_ended(state):
        if node.untried_actions:
            return node, state
        if bot_identity == 1:
            u = max(ucb(child, True) for child in node.child_nodes.values())
            for child in node.child_nodes.values():
                if(ucb(child, True) >= u):
                    best_child = child
        else:
            u = max(ucb(child, False) for child in node.child_nodes.values())
            for child in node.child_nodes.values():
                if(ucb(child, False) >= u):
                    best_child = child
        node = best_child
        state = board.next_state(state, node.parent_action)
    return node, state

def expand_leaf(node: MCTSNode, board: Board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node (if it is non-terminal).

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:
        node: The added child node
        state: The state associated with that node

    """
    action = node.untried_actions.pop()
    next_state = board.next_state(state, action)
    child_node = MCTSNode(parent=node, parent_action=action, action_list=board.legal_actions(next_state))
    node.child_nodes[action] = child_node
    return child_node, next_state

def rollout(board: Board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.
    
    Returns:
        state: The terminal game state

    """
    def find_win(board: Board, state):
        for i in range(2):
            r_owned = 0
            r_empty = []
            c_owned = 0
            c_empty = []
            for j in range(2):
                #checks rows for potential win
                if board.owned_boxes(state)[(i, j)] == board.current_player(state):
                    r_owned += 1
                elif board.owned_boxes(state)[(i, j)] == 0:
                    r_empty.append((i, j))
                #checks cols for potential win
                if board.owned_boxes(state)[(j, i)] == board.current_player(state):
                    c_owned += 1
                elif board.owned_boxes(state)[(j, i)] == 0:
                    c_empty.append((j, i))
            #returns winning action if it exists
            if r_owned == 2 and len(r_empty) == 1:
                return True, r_empty[0][0], r_empty[0][1]
            if c_owned == 2 and len(c_empty) == 1:
                return True, c_empty[0][0], c_empty[0][1]
        return False, None, None

    while not board.is_ended(state):
        Y, X, y, x = choice(board.legal_actions(state))
        win_found, y, x = find_win(board, state)
        if(win_found == True):
            action = Y, X, y, x
            state = board.next_state(state, action)
            continue
        next_action = choice(board.legal_actions(state))
        state = board.next_state(state, next_action)
    return state


def backpropagate(node: MCTSNode|None, won: bool):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    while node is not None:
        node.visits += 1
        if won:
            node.wins += 1
        node = node.parent

def ucb(node: MCTSNode, is_opponent: bool):
    """ Calcualtes the UCB value for the given node from the perspective of the bot

    Args:
        node:   A node.
        is_opponent: A boolean indicating whether or not the last action was performed by the MCTS bot
    Returns:
        The value of the UCB function for the given node
    """
    wi = node.wins
    # if root node, ni will be 0 so need to add edge case
    ni = node.visits
    if ni == 0:
        return float('inf')
    win_rate = wi / ni
    if is_opponent:
        win_rate = 1 - win_rate
    # exploration parameter
    c = explore_faction
    t = node.parent.visits

    return win_rate + c * sqrt(log(t) / ni)

def get_best_action(root_node: MCTSNode):
    """ Selects the best action from the root node in the MCTS tree using UCB criteria

    Args:
        root_node:   The root node

    Returns:
        action: The best action from the root node
    
    """
    best_action = None
    best_ucb_value = -float('inf')

    for action, child_node in root_node.child_nodes.items():
        if child_node.visits == 0:
            ucb_value = float('inf')
        else:
            exploration_factor = sqrt(log(root_node.visits) / child_node.visits)
            win_rate = child_node.wins / child_node.visits
            ucb_value = win_rate + explore_faction * exploration_factor
        
        if ucb_value > best_ucb_value:
            best_ucb_value = ucb_value
            best_action = action

    return best_action


def is_win(board: Board, state, identity_of_bot: int):
    # checks if state is a win state for identity_of_bot
    outcome = board.points_values(state)
    assert outcome is not None, "is_win was called on a non-terminal state"
    return outcome[identity_of_bot] == 1

def think(board: Board, current_state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        current_state:  The current state of the game.

    Returns:    The action to be taken from the current state

    """
    bot_identity = board.current_player(current_state) # 1 or 2
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(current_state))

    for _ in range(num_nodes):
        state = current_state
        node = root_node
        # Do MCTS - This is all you!
        # ...
        node, state = traverse_nodes(node, board, state, bot_identity)

        if not board.is_ended(state):
            node, state = expand_leaf(node, board, state)
        
        end_state = rollout(board, state)
        
        won = is_win(board, end_state, bot_identity)
        backpropagate(node, won)
    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    best_action = get_best_action(root_node)
    print(f"Action chosen: {best_action}")
    return best_action
