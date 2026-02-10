import numpy as np
import random
from .schelling_model import SchellingModel


class SchellingIncomeModel(SchellingModel):
    def __init__(self, grid_size=50, threshold=0.3, empty_ratio=0.1, num_agent_types=2, mean_income=40000, gini_coefficient=0.34):
        self.mean_income = mean_income
        self.gini_coefficient = gini_coefficient
        self.income_groups = list(range(1, 6))
        super().__init__(grid_size, threshold, empty_ratio, num_agent_types) #for some reason if I call the parent init before defining my new variables my code doesn't work?

    def initialize_grid(self):
        total_cells = self.grid_size ** 2
        num_empty = int(total_cells * self.empty_ratio)
        num_agents = total_cells - num_empty

        if num_agents == 0: #avoid calculating income distribution with 0 agents
            return np.array([self.empty] * total_cells).reshape(self.grid_size, self.grid_size)

        #gets n. agents per income group
        income_distribution = self.define_groups(self.mean_income, self.gini_coefficient, num_agents)

        agents = []
        #loops through each income group, assigns agents systematically
        for income_group, count in zip(self.income_groups, income_distribution):
            #evenly distributes income groups across agent types
            for agent_type in self.agent_types:
                agents.extend([int(f"{agent_type}{income_group}")] * (count // len(self.agent_types)))

        #adjusts for leftover agents
        remaining_agents = num_agents - len(agents)
        if remaining_agents > 0:
            for i in range(remaining_agents):
                income_group = self.income_groups[i % len(self.income_groups)]
                agent_type = self.agent_types[i % len(self.agent_types)]
                agents.append(int(f"{agent_type}{income_group}"))

        cells = agents + [self.empty] * num_empty

        random.shuffle(cells)
        return np.array(cells).reshape(self.grid_size, self.grid_size)

    def is_satisfied(self, x, y):
        agent = self.grid[x, y]
        if agent == self.empty:
            return True 

        #separates the two attributes
        agent_type = agent // 10
        agent_income_group = agent % 10

        neighbours = [(x - 1, y - 1), (x - 1, y), (x - 1, y + 1),
                      (x, y - 1),                 (x, y + 1),
                      (x + 1, y - 1), (x + 1, y), (x + 1, y + 1)]


        total_neighbours = 0
        same_agent_type = 0
        income_group_comparison = 0

        for nx, ny in neighbours:
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                neighbour = self.grid[nx, ny]
                if neighbour != self.empty:
                    neighbour_agent_type = neighbour // 10
                    neighbour_income_group = neighbour % 10

                    total_neighbours += 1
                    same_agent_type += (neighbour_agent_type == agent_type)
                    income_group_comparison += (1 - (abs(neighbour_income_group - agent_income_group) / 4)) #weighted on scale 0-1 based on income group disparity

        if total_neighbours == 0:
            return True

        satisfaction = (income_group_comparison + same_agent_type) / (2 * total_neighbours)
        return satisfaction 

    def calculate_mu(self, sigma, mean_income): #for log distribution graph
        return np.log(self.mean_income) - (sigma ** 2) / 2

    #compares generated GC against user input GC
    def calculate_gini(self, array):
        array = np.sort(array)
        index = np.arange(1, array.shape[0] + 1)
        n = array.shape[0]
        return ((np.sum((2 * index - n - 1) * array)) / (n * np.sum(array)))

    def group_by_sigma(self, incomes):
        std_dev = np.std(incomes)
        negative_sigma = self.mean_income - std_dev
        positive_sigma = self.mean_income + std_dev
        positive_sigma2 = self.mean_income + 2 * std_dev

        negative_sigma_index = np.searchsorted(incomes, negative_sigma)
        mean_income_index = np.searchsorted(incomes, self.mean_income)
        positive_sigma_index = np.searchsorted(incomes, positive_sigma)
        positive_sigma2_index = np.searchsorted(incomes, positive_sigma2)

        groups = [
            int(negative_sigma_index),
            int(mean_income_index - negative_sigma_index),
            int(positive_sigma_index - mean_income_index),
            int(positive_sigma2_index - positive_sigma_index),
            int(len(incomes) - positive_sigma2_index)
        ]

        return groups

    def define_groups(self, mean_income, gini_coefficient, num_agents):
        if gini_coefficient < 0.03: #perfect equality
            return [num_agents, 0, 0, 0, 0]

        if gini_coefficient > 0.97: #perfect inequality
            return [num_agents - 1, 0, 0, 0, 1]

        #determine sigma range based on gini coefficient
        if gini_coefficient < 0.3:
            left, right = 0.1, 1.0
        elif gini_coefficient > 0.7:
            left, right = 0.5, 3.0  
        else:
            left, right = 0.1, 2.0 

        #binary search to adjust sigma
        tolerance = 0.01
        best_sigma = (left + right) / 2

        iteration = 0
        max_iterations = 100
        while right - left > tolerance and iteration < max_iterations:          
            sigma = (left + right) / 2
            mu = self.calculate_mu(sigma, self.mean_income)  
            incomes = np.random.lognormal(mean=mu, sigma=sigma, size=num_agents)
            calculated_gini = self.calculate_gini(incomes)

            if abs(calculated_gini - self.gini_coefficient) < tolerance:
                best_sigma = sigma
                break
            elif calculated_gini > self.gini_coefficient:
                right = sigma 
            else:
                left = sigma 

        #final distribution with best sigma
        mu = self.calculate_mu(best_sigma, self.mean_income)
        incomes = np.random.lognormal(mean=mu, sigma=best_sigma, size=num_agents)
        sorted_incomes = np.sort(incomes)

        return self.group_by_sigma(sorted_incomes)
