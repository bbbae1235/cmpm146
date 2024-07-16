import sys
sys.path.insert(0, '../')
from planet_wars import issue_order


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)

# def spread_to_weakest_neutral_planet(state):
#     # (1) If we currently have a fleet in flight, just do nothing.
#     if len(state.my_fleets()) >= 1:
#         return False

#     # (2) Find my strongest planet.
#     strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

#     # (3) Find the weakest neutral planet.
#     weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

#     if not strongest_planet or not weakest_planet:
#         # No legal source or destination
#         return False
#     else:
#         # (4) Send half the ships from my strongest planet to the weakest enemy planet.
#         return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)
    
def spread_to_weakest_neutral_planet(state):
    # If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # strong_planet = [p for p in state.my_planets() if p.num_ships >= 30]
    strong_planet = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)

    # List of neutral planets sorted by number of ships (weakest first)
    neutral_planet = sorted(state.neutral_planets(), key=lambda p: p.num_ships)

    if not strong_planet or not neutral_planet:
        return False
    else:
        success = False
        for i in strong_planet:
            for j in neutral_planet:
                # If strong planet has 50 ships, send half to neutral planet
                if i.num_ships >= j.num_ships + 20:
                    success = issue_order(state, i.ID, j.ID, j.num_ships + 1) or success
            # If strong planet has less, don't do anything
            if i.num_ships <= j.num_ships:
                break
        return success
    
def defend(state):
    if len(state.my_fleets()) >= 1:
        return False
    # Find my planet that is under threat
    threatened_planet = None
    enemy_fleet_size = None
    for planet in state.my_planets():
        for fleet in state.enemy_fleets():
            if fleet.destination_planet == planet.ID:
                threatened_planet = planet
                enemy_fleet_size = fleet.num_ships
                break

    if not threatened_planet:
        return False

    # Find the strongest planet that can send reinforcements
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or strongest_planet.ID == threatened_planet.ID:
        return False

    # Send reinforcements to the threatened planet
    num_ships_to_send = min(strongest_planet.num_ships // 2, threatened_planet.num_ships)
    if num_ships_to_send > enemy_fleet_size:
        return issue_order(state, strongest_planet.ID, threatened_planet.ID, num_ships_to_send)
    return False

def take_over(state):
    # If there is already a fleet in flight, do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # List of my planets sorted by number of ships (strongest first).
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    if not my_planets:
        return False

    # List of untargeted planets (both neutral and enemy)
    target_planets = []
    for planet in state.not_my_planets():
        targeted = any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())
        if not targeted:
            target_planets.append(planet)

    # Sort target planets by number of ships (ascending)
    target_planets.sort(key=lambda p: p.num_ships)

    if not target_planets:
        return False
    
    success = False
    for target_planet in target_planets:
        total_ships_needed = target_planet.num_ships + 1
        if target_planet.owner != 0:
            total_ships_needed += state.distance(my_planets[0].ID, target_planet.ID) * target_planet.growth_rate
        
        # Gather ships from multiple planets
        ships_to_send = 0
        for my_planet in my_planets:
            if ships_to_send >= total_ships_needed:
                break
            ships_from_this_planet = min(my_planet.num_ships // 2, total_ships_needed - ships_to_send)
            if ships_from_this_planet > 0:
                success = issue_order(state, my_planet.ID, target_planet.ID, ships_from_this_planet) or success
                ships_to_send += ships_from_this_planet

        # Remove the target planet if it is successfully targeted.
        if ships_to_send >= total_ships_needed:
            target_planets.remove(target_planet)

    return success
