import random
from colorama import Fore, Style, init
init(autoreset=True)


def decide_direction(foods, agent):

    # =====================================================
    # 1. REAL FOOD VISIBLE → GO TO NEAREST FOOD
    # =====================================================
    if foods:
        min_distance = 100
        nearest_food = None

        for food in foods:
            fx, fy = food
            distance = abs(fx - agent.x) + abs(fy - agent.y)

            if distance < min_distance:
                nearest_food = food
                min_distance = distance

        fx, fy = nearest_food
        print(Fore.YELLOW + f"{agent.name} is moving to food at {fx, fy}")

        if fx > agent.x:
            return "right"
        elif fx < agent.x:
            return "left"
        elif fy > agent.y:
            return "up"
        elif fy < agent.y:
            return "down"


    # =====================================================
    # 2. PANIC MODE → SURVIVE AT ANY COST
    # =====================================================
    elif agent.mode == "Panic" and agent.memory:

        # Very low energy → random desperate movement
        if agent.energy < 3:
            print(Fore.RED + f"{agent.name} CRITICAL ENERGY → desperate search")
            return random.choice(["up", "down", "left", "right"])

        # Otherwise go to nearest memory
        min_distance = 999
        target = None

        for fx, fy, age in agent.memory:
            distance = abs(agent.x - fx) + abs(agent.y - fy)

            if distance < min_distance:
                min_distance = distance
                target = (fx, fy)

        if target:
            fx, fy = target
            print(Fore.RED + f"{agent.name} PANIC → heading to nearest memory {target}")

            if fx > agent.x:
                return "right"
            elif fx < agent.x:
                return "left"
            elif fy > agent.y:
                return "up"
            elif fy < agent.y:
                return "down"


    # =====================================================
    # 3. NORMAL MEMORY MODE (SMART MEMORY)
    # Choose memory based on distance + age
    # =====================================================
    elif agent.memory:
        best_score = 999
        target = None

        for fx, fy, age in agent.memory:
            distance = abs(fx - agent.x) + abs(fy - agent.y)

            # Old memories become less important
            score = distance + (age * 2)

            if score < best_score:
                best_score = score
                target = (fx, fy)

        if target:
            fx, fy = target
            print(Fore.LIGHTMAGENTA_EX +
                  f"{agent.name} is using his smart memory and heading to {target}")

            if fx > agent.x:
                return "right"
            elif fx < agent.x:
                return "left"
            elif fy > agent.y:
                return "up"
            elif fy < agent.y:
                return "down"


    # =====================================================
    # 4. EXPLORATION AI (No food, no memory)
    # This is the important AI part
    # Agent evaluates ALL 4 directions and chooses the BEST
    # =====================================================
    else:
        print("Exploring")

        # Possible moves and their resulting positions
        directions = {
            "up": (agent.x, agent.y + 1),
            "down": (agent.x, agent.y - 1),
            "left": (agent.x - 1, agent.y),
            "right": (agent.x + 1, agent.y)
        }

        # List of places already visited
        visited_cells = [(vx, vy) for vx, vy, _ in agent.visited]

        best_score = -999
        best_direction = None

        # Check each possible direction
        for direction, (nx, ny) in directions.items():

            # Ignore moves outside grid
            if not (0 <= nx <= 9 and 0 <= ny <= 9):
                continue

            score = 0

            # Prefer new areas
            if (nx, ny) not in visited_cells:
                score += 5
            else:
                score -= 2

            # Move toward remembered food locations (weak attraction)
            for fx, fy, age in agent.memory:
                dist = abs(nx - fx) + abs(ny - fy)
                score += 3 / (dist + 1 + age)

            # Low energy → stronger attraction to memory
            if agent.energy < 5:
                score *= 1.5

            # Keep best direction
            if score > best_score:
                best_score = score
                best_direction = direction

        # If a best direction found → use it
        if best_direction:
            print(Fore.LIGHTRED_EX +
                  f"{agent.name} exploring smartly → {best_direction}")
            return best_direction

        # Fallback (should rarely happen)
        print(Fore.BLUE + f"{agent.name} moving randomly")
        return random.choice(["up", "down", "left", "right"])
