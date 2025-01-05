import copy
import time


# defining initial state

initial_bays = [[(3, "heavy"), ], [(1, "light"), (6, "light"),], [], [(4, "light"),  (2, "heavy"), (5, "light")], [], []]
initial_crane_position = 0
initial_crane_container_held = 0
initial_cost = 0

initial_state = ([initial_bays, initial_crane_position, initial_crane_container_held], 0)


def print_state(state_and_time):
    state = state_and_time[0]
    for i in range(len(state[0])):
        if i == state[1]:
            print(str(state[0][i])+" <-["+str(state[2])+"]-")
        else:
            print(str(state[0][i]))
    print("Total cost: "+str(state_and_time[1]))
    print()


def perform_action(state, action):
    new_state = copy.deepcopy(state[0])  # Copy the entire state (bays, crane position, container held)

    new_state_cost = state[1]  # Track the current cost
    if action == "RIGHT":
        if new_state[1] >= (len(new_state[0]) - 1):  # If already at the rightmost bay
            return None
        new_state[1] += 1  # Move crane to the right
        cost = 3
        if new_state[2] != 0:
            if new_state[2][1] == "heavy":
                cost += 1
    elif action == "LEFT":
        if new_state[1] <= 0:  # If already at the leftmost bay
            return None
        new_state[1] -= 1  # Move crane to the left
        cost = 3
        if new_state[2] != 0:
            if new_state[2][1] == "heavy":
                cost += 1
    elif action == "DROP":

        if new_state[2] == 0:  # If no container is held
            return None
        if len(new_state[0][new_state[1]]) >= 4:  # Check if the current bay has already 4 containers
            return None
        cost = 5 - len(new_state[0][new_state[1]])  # cost based on num of containers before drop off
        container = new_state[2]
        new_state[2] = 0  # Drop the container
        new_state[0][new_state[1]].append(container)  # Add the container to the current bay
    elif action == "PICK":
        if new_state[2] != 0:  # If a container is already held
            return None
        if len(new_state[0][new_state[1]]) == 0:  # If no containers in the current bay
            return None
        cost = 5 - len(new_state[0][new_state[1]])  # cost based on num of containers before pick up
        container = new_state[0][new_state[1]].pop()  # Pick up the top container
        new_state[2] = container
    else:
        return None  # Invalid action

    return new_state, new_state_cost + cost


def perform_action_sequence(state, actions):
    new_state = state
    for action in actions:
        print(f"Performing action: {action}")
        result = perform_action(new_state, action)
        if result is None:  # If the action is invalid, stop processing
            print(f"Action '{action}' is invalid in the current state.")
            return None
        new_state = result  # Update the state to the result of the action
        print_state(new_state)  # Print the state after each action
    print(f"Actions taken: {actions}")
    return new_state


def is_goal_state(state):
    bays, crane_position, crane_container_held = state[0]

    # Iterate through the bays
    for i, bay in enumerate(bays):
        # Check if this bay contains containers 1, 2, and 3 in order
        if [container[0] for container in bay] == [1, 2, 3]:
            # Check if the crane is not in the same bay
            if crane_position != i:
                return True

    # If we haven't returned True by now, it's not a goal state
    return False


all_actions = ["DROP", "PICK", "LEFT", "RIGHT"]


# use to validate the agent's action
def is_action_valid(state, action):
    if perform_action(state, action):
        return True
    else:
        return False


def heuristic_function(previous_state, current_state):
    estimated_cost = 0
    # Initialize the dictionary to store bay indices for containers 1, 2, and 3
    current_bay_indices = {1: None, 2: None, 3: None}
    previous_bay_indices = {1: None, 2: None, 3: None}

    # check if containers are in crane and update bay indices according to crane position
    if current_state[0][2] != 0:
        container_id = current_state[0][2][0]
        if container_id in current_bay_indices:
            current_bay_indices[container_id] = current_state[0][1]
    if previous_state is not None and previous_state[0][2] != 0:
        container_id = previous_state[0][2][0]
        if container_id in previous_bay_indices:
            previous_bay_indices[container_id] = previous_state[0][1]

    # Loop through the rest of the bays and update the bay indices for containers 1, 2, and 3
    for i, bay in enumerate(current_state[0][0]):
        for container in bay:
            if container[0] in current_bay_indices:
                current_bay_indices[container[0]] = i
    if previous_state is not None:
        for i, bay in enumerate(previous_state[0][0]):
            for container in bay:
                if container[0] in previous_bay_indices:
                    previous_bay_indices[container[0]] = i

    # checks on container 1
    current_bay_index_1 = current_bay_indices[1]
    previous_bay_index_1 = previous_bay_indices[1]

    if current_bay_index_1 is not None:
        bay_at_index_1 = current_state[0][0][current_bay_index_1]

        for idx, container in enumerate(bay_at_index_1):
            # check if container 1 is not the lowest (increase cost)
            if container[0] == 1:
                if idx > 0:
                    estimated_cost += 1
                elif idx == 0:
                    estimated_cost -= 2
                # check how many containers are on top of 1 that are not 2 (increase cost)
                if idx + 1 < len(bay_at_index_1):
                    if not bay_at_index_1[idx + 1][0] == 2:
                        estimated_cost += len(bay_at_index_1) - idx - 1
        if current_state[0][2] != 0 and current_state[0][2][0] == 1 and current_state[0][1] == current_bay_index_1 \
                and len(bay_at_index_1) == 0:
            estimated_cost -= 2

    if previous_bay_index_1 is not None:
        bay_at_index_1 = previous_state[0][0][previous_bay_index_1]
        containers_above_1 = []
        # check if container 1 is picked up when it was in wrong position (decrease) when in correct position (increase)
        for idx, container in enumerate(bay_at_index_1):
            if container[0] == 1:
                containers_above_1 = bay_at_index_1[idx + 1:]
                if current_state[0][2] != 0 and current_state[0][2][0] == 1:
                    if idx > 0:
                        estimated_cost -= 2
                    else:
                        estimated_cost += 2
        # check if trying to pick up a container that was previously bocking 1 (decrease cost)
        if current_state[0][2] != 0:
            crane_container = current_state[0][2]  # Container in the crane
            for container in containers_above_1:
                if container == crane_container:
                    estimated_cost -= 2

    # checks on container 2
    current_bay_index_2 = current_bay_indices[2]
    previous_bay_index_2 = previous_bay_indices[2]
    if current_bay_index_2 is not None:
        # check distance to container 1
        estimated_cost += abs(current_bay_index_2 - current_bay_index_1)
        bay_at_index_2 = current_state[0][0][current_bay_index_2]
        for idx, container in enumerate(bay_at_index_2):
            if container[0] == 2:
                # check if container 2 is in the same bay as 1 but not above it
                if current_bay_index_2 == current_bay_index_1 and idx > 0 and bay_at_index_2[idx - 1][0] != 1:
                    estimated_cost += 1
                    estimated_cost += len(bay_at_index_2) - idx - 1

    if previous_bay_index_2 is not None:
        # checks if the crane picked up container 3
        if current_state[0][2] != 0 and current_state[0][2][0] == 2:
            # checks if container 2 was in same bay as 1
            if previous_bay_index_2 == current_bay_index_1:
                bay_at_index_1 = previous_state[0][0][previous_bay_index_1]
                for idx, container in enumerate(bay_at_index_1):
                    if container[0] == 1:
                        # if container 1 was at the right position increase cost
                        if idx == 0 and idx + 1 < len(bay_at_index_1) and bay_at_index_1[idx + 1][0] == 2:
                            estimated_cost += 2
                        # if container 1 was in the wrong position increase cost
                        elif idx > 0 and idx + 1 < len(bay_at_index_1) and bay_at_index_1[idx + 1][0] != 2:
                            estimated_cost -= 2
                # checks if container 2 was not above 1
            elif previous_bay_index_2 != current_bay_index_1:
                estimated_cost -= 2

    # checks on container 3
    current_bay_index_3 = current_bay_indices[3]
    previous_bay_index_3 = previous_bay_indices[3]
    if current_bay_index_3 is not None:
        # check distance to container 1
        estimated_cost += abs(current_bay_index_3 - current_bay_index_1)
        bay_at_index_3 = current_state[0][0][current_bay_index_3]
        for idx, container in enumerate(bay_at_index_3):
            if container[0] == 3:
                # check if container 3 is in the same bay as 1 and not above it 2 and 1
                if current_bay_index_3 == current_bay_index_1 and idx > 0 and bay_at_index_3[idx - 1][0] != 2 \
                        and bay_at_index_3[idx - 2][0] != 1:
                    estimated_cost += 1
                    estimated_cost += len(bay_at_index_3) - idx - 1

    if previous_bay_index_3 is not None:
        # checks if the crane picked up container 3
        if current_state[0][2] != 0 and current_state[0][2][0] == 3:
            # checks if container 3 was above 2
            if previous_bay_index_3 == current_bay_index_1 == current_bay_index_2:
                bay_at_index_1 = previous_state[0][0][current_bay_index_1]
                for idx, container in enumerate(bay_at_index_1):
                    if container[0] == 1:
                        # if container 1 was at the right position increase cost
                        if idx == 0 and idx + 1 < len(bay_at_index_1) and bay_at_index_1[idx + 1][0] == 2 and idx + 2 < len(bay_at_index_1) and bay_at_index_1[idx + 2][0] == 3:
                            estimated_cost += 2
                        # if container 1 was in the wrong position decrease cost
                        elif idx > 0 or (idx + 1 < len(bay_at_index_1) and bay_at_index_1[idx + 1][0] != 2) or (idx + 2 < len(bay_at_index_1) and bay_at_index_1[idx + 2][0] != 3):
                            estimated_cost -= 2
            # checks if container 3 was not in same bay as 1 2
            elif previous_bay_index_3 != current_bay_index_1 and previous_bay_index_3 != current_bay_index_2:
                estimated_cost += 2
    return estimated_cost


def astar(initial_state, possible_actions=all_actions):
    frontier = {}  # store states to be explored
    explored_states = []  # store states already explored

    initial_g = initial_state[1]
    initial_h = heuristic_function(None, initial_state)

    start = time.time()  # Time tracking restored

    # Hash the initial state
    state_hash = hash(str(initial_state))
    frontier[state_hash] = (initial_g + initial_h, (initial_state, []))

    while frontier:
        # Find the state with the smallest f-cost
        current_state_hash = min(frontier, key=lambda x: frontier[x][0])
        current_f, (state, actions) = frontier.pop(current_state_hash)

        # Mark the state as explored
        if tuple(state[0]) not in explored_states:  # Convert state[0] to tuple
            explored_states.append(tuple(state[0]))

        # Check if goal state is reached
        if is_goal_state(state):
            print("Initial State:")
            print_state(initial_state)
            print("Goal found:", str(actions).replace("[", "").replace("]", ""))
            perform_action_sequence(initial_state, actions)
            return True

        # Explore the next states
        for action in possible_actions:
            if is_action_valid(state, action):
                new_state = perform_action(state, action)

                # Skip already explored states
                if tuple(new_state[0]) in explored_states:
                    continue

                # Calculate costs
                new_g_cost = state[1] + new_state[1]
                new_h_cost = heuristic_function(state, new_state)
                new_f_cost = new_g_cost + new_h_cost

                # Hash the new state
                new_state_hash = hash(str(new_state))

                # Add the new state to the frontier
                frontier[new_state_hash] = (new_f_cost, (new_state, actions + [action]))

        # Check for timeout
        end = time.time()
        if end - start > 20:
            raise TimeoutError("Execution is taking too long to terminate.")


astar(initial_state)
