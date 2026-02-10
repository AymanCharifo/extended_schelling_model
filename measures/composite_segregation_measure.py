import numpy as np
from collections import defaultdict
from itertools import combinations


class CompositeSegregationMeasure:
    def __init__(self, grid, num_agent_types, empty_ratio, is_income_model=False):
        self.grid = grid
        self.grid_size = grid.shape[0]
        self.empty = -1 #to pass into isolations's is_satisfied function
        self.num_agent_types = num_agent_types
        self.empty_ratio = empty_ratio
        self.is_income_model = is_income_model
        
    def calculate_isolation_index(self):
        # Import here to avoid circular imports
        from models import SchellingModel, SchellingIncomeModel
        
        if self.empty_ratio == 1:
            return 0

        isolation_indices = []

        for x in range(self.grid_size):
            for y in range(self.grid_size):
                if self.is_income_model:
                    isolation_indices.append(SchellingIncomeModel.is_satisfied(self, x, y))
                else:
                    isolation_indices.append(SchellingModel.is_satisfied(self, x, y))
                
        #calculates the mean isolation index
        isolation_index = np.mean(isolation_indices) if isolation_indices else 0
        return isolation_index


    def calculate_morans_i(self):
        if self.empty_ratio == 1:
            return 0

        total_cells = self.grid_size ** 2
        num_empty = int(total_cells * self.empty_ratio)
        num_agents = total_cells - num_empty

        #for np calcs
        agent_type_list = []
        agent_income_group_list = []

        for x in range(self.grid_size):
            for y in range(self.grid_size):
                agent = self.grid[x, y]
                if agent == self.empty:  
                    continue

                if self.is_income_model:
                    agent_type = agent // 10
                    agent_income_group = agent % 10
                    agent_type_list.append(agent_type)
                    agent_income_group_list.append(agent_income_group)
                else:
                    agent_type = agent
                    agent_type_list.append(agent_type)

        #calculate means and standard deviations
        xbar_agent_type = np.mean(agent_type_list)

        if self.is_income_model:
            agent_type_std_dev = np.std(agent_type_list)
            
            xbar_income_group = np.mean(agent_income_group_list)
            agent_income_group_std_dev = np.std(agent_income_group_list)

        #check for zero standard deviation
        if self.is_income_model:
            if agent_type_std_dev == 0:
                return 0
            if agent_income_group_std_dev == 0:
                return 0

        #initialise main variables
        numerator = 0
        denominator = 0
        W = 0

        for x in range(self.grid_size):
            for y in range(self.grid_size):
                agent = self.grid[x, y]
                if agent == self.empty: 
                    continue

                if self.is_income_model:
                    agent_type = agent // 10
                    agent_income_group = agent % 10
                else:
                    agent_type = agent

                #standardize attributes
                if self.is_income_model:
                    standardised_agent_type = (agent_type - xbar_agent_type) / agent_type_std_dev
                    standardised_agent_income_group = (agent_income_group - xbar_income_group) / agent_income_group_std_dev
                    agent_composite = (standardised_agent_type + standardised_agent_income_group) / 2
                else:
                    agent_composite = (agent_type - xbar_agent_type)

                #add to denominator
                denominator += agent_composite ** 2
                
                neighbours = [            (x - 1, y),
                          (x, y - 1),                 (x, y + 1),
                                          (x + 1, y)                ]

                for nx, ny in neighbours:
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                        neighbour = self.grid[nx, ny]
                        if neighbour != self.empty:
                            W += 1
                            if self.is_income_model:
                                neighbour_agent_type = neighbour // 10
                                neighbour_income_group = neighbour % 10
                                
                                standardised_neighbour_agent_type = (neighbour_agent_type - xbar_agent_type) / agent_type_std_dev
                                standardised_neighbour_income_group = (neighbour_income_group - xbar_income_group) / agent_income_group_std_dev

                                neighbour_composite = (standardised_neighbour_agent_type + standardised_neighbour_income_group) / 2
                            else:
                                neighbour_agent_type = neighbour
                                neighbour_composite = (neighbour_agent_type - xbar_agent_type)

                            numerator += agent_composite * neighbour_composite

        #caculating morans
        if W == 0 or denominator == 0:
            return 0

        morans_i = (num_agents * numerator) / (W * denominator)
        return morans_i


    def calculate_dissimilarity_index(self):
        if self.empty_ratio == 1:
            return 0

        #initialise dictionaries to store counts
        row_agent_counts = defaultdict(lambda: defaultdict(int))# row: agent type: count
        total_agent_counts = defaultdict(int)# agent type: total count

        if self.is_income_model:
            row_income_counts = defaultdict(lambda: defaultdict(int))# row: income group: count
            total_income_counts = defaultdict(int)# income group: total count

        #counts agent types and income groups if applicable per row
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                agent = self.grid[x, y]
                if agent == self.empty:  # Skip empty cells
                    continue

                # Extract agent type and income group (if applicable)
                if self.is_income_model:
                    agent_type = agent // 10
                    income_group = agent % 10
                else:
                    agent_type = agent

                # Update counts for agent types
                row_agent_counts[x][agent_type] += 1
                total_agent_counts[agent_type] += 1

                # Update counts for income groups (if applicable)
                if self.is_income_model:
                    row_income_counts[x][income_group] += 1
                    total_income_counts[income_group] += 1

        #calculates the permutation sum for each row, sums up total
        agent_types = list(range(1, self.num_agent_types + 1))
        agent_diff_sum = 0
        agent_permutations = 0

        for row in range(self.grid_size):
            row_agent_pairs = list(combinations(agent_types, 2))#all pair combinations
            for (i, j) in row_agent_pairs:
                count_i = row_agent_counts[row].get(i, 0)
                count_j = row_agent_counts[row].get(j, 0)
                total_i = total_agent_counts[i]
                total_j = total_agent_counts[j]

                if count_i == 0 or count_j == 0:
                    continue #skips if region does not have the agent type

                diff = abs((count_i / total_i) - (count_j / total_j))
                agent_diff_sum += diff
                agent_permutations += 1
        agent_diff_sum /= agent_permutations

        #if applicable calculates the permutation sum for each row, sums up total
        if self.is_income_model:
            income_groups = list(total_income_counts.keys())
            income_diff_sum = 0
            income_permutations = 0

            for row in range(self.grid_size):
                row_income_pairs = list(combinations(income_groups, 2))  
                for (i, j) in row_income_pairs:
                    count_i = row_income_counts[row].get(i, 0)
                    count_j = row_income_counts[row].get(j, 0)
                    total_i = total_income_counts[i]
                    total_j = total_income_counts[j]

                    if count_i == 0 or count_j == 0:
                        continue #skips if region does not have the income group

                    diff = abs((count_i / total_i) - (count_j / total_j))
                    income_diff_sum += diff
                    income_permutations += 1
            income_diff_sum /= income_permutations

        if self.is_income_model:
            dissimilarity_index = (agent_diff_sum + income_diff_sum) / 4
        else:
            dissimilarity_index = agent_diff_sum / 2
        return dissimilarity_index


    def calculate_composite_segregation_measure(self):
        #x-axis
        isolation_index = self.calculate_isolation_index()
        exposure_index = 1 - isolation_index

        composite_x_axis = exposure_index - isolation_index if isolation_index else 0

        #y-axis
        morans_i = self.calculate_morans_i()
        dissimilarity_index = self.calculate_dissimilarity_index()

        composite_y_axis = dissimilarity_index - morans_i

        composite_segregation_measure = f'({composite_x_axis:.5f} , {composite_y_axis:.5f})'
        return composite_segregation_measure
