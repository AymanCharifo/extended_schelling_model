import numpy as np
import random


class SchellingModel:
    def __init__(self, grid_size=50, threshold=0.3, empty_ratio=0.1, num_agent_types=2): #default initial grid
        self.grid_size = grid_size
        self.threshold = threshold
        self.empty_ratio = empty_ratio
        self.empty = -1
        self.agent_types = list(range(1, num_agent_types + 1))
        self.num_agent_types = num_agent_types
        self.grid = self.initialize_grid()
        self.dissatisfied_agents = self.get_dissatisfied_agents()

    def initialize_grid(self):
        #calculate amount of agents
        total_cells = self.grid_size ** 2
        num_empty = int(total_cells * self.empty_ratio)
        num_agents = total_cells - num_empty

        #distributes all agent types equally
        num_per_type = num_agents // self.num_agent_types
        remaining_agents = num_agents % self.num_agent_types

        #1D array of grid
        cells = [self.empty] * num_empty
        for agent_type in self.agent_types:
            cells.extend([agent_type] * num_per_type)
        cells.extend([random.choice(self.agent_types) for i in range(remaining_agents)])

        #shuffles cells and makes the grid 2D
        random.shuffle(cells)
        return np.array(cells).reshape(self.grid_size, self.grid_size)

    def is_satisfied(self, x, y):
        agent = self.grid[x, y]
        if agent == self.empty:
            return True #empty cells always satisfied

        neighbours = [(x - 1, y - 1), (x - 1, y), (x - 1, y + 1),
                      (x, y - 1),                 (x, y + 1),
                      (x + 1, y - 1), (x + 1, y), (x + 1, y + 1)]

        same_agent_type = 0
        total_neighbours = 0

        for nx, ny in neighbours:
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size: #ensures nx ny in grid, removes invalid values
                neighbour = self.grid[nx, ny]
                if neighbour != self.empty: #if neighbour not empty, increment neighbour. if same type, increment 
                    total_neighbours += 1
                    same_agent_type += (neighbour == agent)

        if total_neighbours == 0:
            return True

        satisfaction = same_agent_type / total_neighbours
        return satisfaction 

    def get_dissatisfied_agents(self):
        dissatisfied_agents = []
        #iterates through every agent
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                if not (self.is_satisfied(x, y) >= self.threshold):
                    dissatisfied_agents.append((x, y))
        return dissatisfied_agents

    def find_empty_cell(self):
        empty_cells = np.argwhere(self.grid == self.empty) 
        return tuple(empty_cells[random.randint(0, len(empty_cells) - 1)]) if len(empty_cells) > 0 else None

    def step(self):
        moved = False
        for x, y in self.dissatisfied_agents:
            empty_cell = self.find_empty_cell()
            if empty_cell:
                ex, ey = empty_cell
                self.grid[ex, ey], self.grid[x, y] = self.grid[x, y], self.empty #swaps positions
                moved = True
        if moved:
            self.dissatisfied_agents = self.get_dissatisfied_agents() 
        return moved

    def calculate_satisfaction(self):
        total_agents = np.count_nonzero(self.grid != self.empty)
        satisfied_agents = total_agents - len(self.dissatisfied_agents)
        return round((satisfied_agents / total_agents) * 100, 2) if total_agents > 0 else 100
