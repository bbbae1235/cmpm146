
from mcts_node import MCTSNode
from p2_t3 import Board
from random import choice
from math import sqrt, log

num_nodes = 100
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
    while board.is_ended(state):
        if node.untried_actions:
            return node, state
        u = max(ucb(child, True) for child in node.child_nodes.values())
        for child in node.child_nodes.values():
            if(ucb(child, True) >= u):
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
    if not board.is_ended(state):
        new_action = choice(node.untried_actions)
        new_state = board.next_state(state, new_action)
        new_node = MCTSNode(parent=node, parent_action=new_action, action_list=board.legal_actions(new_state))
        node.child_nodes[new_action] = new_node
        node.untried_actions.remove(new_action)
        return new_node, new_state
    return node, state

    '''
    # if the current state of the game isn't a win/draw (terminal state), then create a new node object and add it to the 
    # node's child dictionary
    if (not(board.is_ended(state))):
        new = MCTSNode()
        node.child_nodes[state] = new
        return new, state
    '''

def rollout(board: Board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.
    
    Returns:
        state: The terminal game state

    """
    
    # if the terminal state has been reached, return it
    while not board.is_ended(state):
        # generate  random state 
        random_move = choice(board.legal_actions(state))
        state = board.next_state(state,random_move)
     # when the terminal state has been reached, return it
    return state
    '''
    # if the terminal state has been reached, return it
    if (board.is_ended):
        return state
    
    # generate first random next state
    random_move = choice(board.legal_actions(state))
    # while terminal state has not been reached (game has not ended)
    while (not(board.is_ended)):
        # generate a new random state given the previous random state
        random_move = choice(board.legal_actions(random_move))
    # when the terminal state has been reached, return it
    return random_move
    '''


def backpropagate(node: MCTSNode|None, won: bool):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    # Start at current
    # Check for wins and visits
    # Confirm you haven't gone past node and keep moving up the tree
    current = node  # Start with node where simluation ends and backpropagation begins
    while current is not None:  # work backwards up to the root
        current.visits += 1  # Increment  visit count for  current node
        # If  bot wins, increment win count
        if won:  
            current.wins += 1
        current = current.parent  # Move to parent node

# def ucb(node: MCTSNode, is_opponent: bool):
def ucb(child: MCTSNode, current: MCTSNode, is_opponent: bool):
    """ Calcualtes the UCB value for the given node from the perspective of the bot

    Args:
        node:   A node.
        is_opponent: A boolean indicating whether or not the last action was performed by the MCTS bot
    Returns:
        The value of the UCB function for the given node
    """
    # win rate + explore_faction(sqrt(lnt/visits))
    # if this is the opponent's perspective, then take the inverse of the bot's win rate
    if (is_opponent):
        win_rate = child.wins / child.visits
    else:
        win_rate = (1 - child.wins) / child.visits

    exploration = explore_faction * (sqrt(log(current.visits) / child.visits))
    return (win_rate + exploration)

def get_best_action(root_node: MCTSNode, is_opponent: bool):
    """ Selects the best action from the root node in the MCTS tree

    Args:
        root_node:   The root node
    Returns:
        action: The best action from the root node
    
    """
    largest_uct = -1
    best = None
    best_action = None
    current_uct = -1

    # calculate the uct of each child
    for action, child in (root_node.child_nodes).items():
        current_uct = ucb(child, root_node, is_opponent)
        # if the current child's uct is greater than the greatest recorded uct and the child is expandable, then overwrite 
        # the largest uct
        if (current_uct > largest_uct and child.untried_actions != 0):
            largest_uct = current_uct
            best = child
            best_action = action
    return best, best_action

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

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    _, best_action = get_best_action(root_node, False)
    print(f"Action chosen: {best_action}")
    return best_action