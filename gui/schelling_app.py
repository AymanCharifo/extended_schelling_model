import tkinter as tk
from models import SchellingModel, SchellingIncomeModel
from measures import CompositeSegregationMeasure
from utils import COLOURS


class SchellingApp:
    def __init__(self, master, model, is_income_model=False):
        self.master = master
        self.model = model
        self.running = False
        self.rounds = 0
        self.is_income_model = is_income_model

        self.canvas_size = 500
        self.cell_size = self.canvas_size / self.model.grid_size

        #creates main layout
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        #side panel for extended model
        if self.is_income_model:
            self.side_frame = tk.Frame(master)
            self.side_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

            #gini coefficient slider
            self.gini_slider = tk.Scale(self.side_frame, from_=0.0, to=1.0, resolution=0.01,
                                        orient=tk.HORIZONTAL, label="Gini Coefficient", command=self.update_gini_coefficient)
            self.gini_slider.set(self.model.gini_coefficient) 
            self.gini_slider.pack(fill=tk.X, pady=5)

            #mean income slider
            self.mean_income_slider = tk.Scale(self.side_frame, from_=1000, to=100000, resolution=500,
                                               orient=tk.HORIZONTAL, label="Mean Income ($)", command=self.update_mean_income)
            self.mean_income_slider.set(self.model.mean_income)
            self.mean_income_slider.pack(fill=tk.X, pady=5)

        #canvas
        self.canvas = tk.Canvas(self.main_frame, width=self.canvas_size, height=self.canvas_size)
        self.canvas.grid(row=0, column=0, columnspan=4, pady=10)

        #satisfaction level + number of rounds
        self.satisfaction_label = tk.Label(self.main_frame, text="Satisfied Agents: 100%")
        self.satisfaction_label.grid(row=1, column=0, columnspan=2)

        self.rounds_label = tk.Label(self.main_frame, text="Rounds: 0")
        self.rounds_label.grid(row=1, column=2, columnspan=2)

        #sets control buttons and sliders
        self.create_controls()

    def create_controls(self):
        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.grid(row=2, column=0, columnspan=4)

        self.threshold_slider = tk.Scale(self.control_frame, from_=0.0, to=1.0, resolution=0.01,
                                         orient=tk.HORIZONTAL, label="Threshold Level", command=self.update_threshold)
        self.threshold_slider.set(self.model.threshold)
        self.threshold_slider.pack(side=tk.LEFT, padx=5)

        self.empty_slider = tk.Scale(self.control_frame, from_=0.0, to=1.0, resolution=0.01,
                                     orient=tk.HORIZONTAL, label="Empty Space (%)", command=self.update_empty_ratio)
        self.empty_slider.set(self.model.empty_ratio)
        self.empty_slider.pack(side=tk.LEFT, padx=5)

        self.grid_size_slider = tk.Scale(self.control_frame, from_=10, to=125, resolution=1,
                                         orient=tk.HORIZONTAL, label="Grid Size (NxN)", command=self.update_grid_size)
        self.grid_size_slider.set(self.model.grid_size)
        self.grid_size_slider.pack(side=tk.LEFT, padx=5)

        self.agent_type_slider = tk.Scale(self.control_frame, from_=2, to=4, resolution=1,
                                          orient=tk.HORIZONTAL, label="No. Agent Types", command=self.update_agent_types)
        self.agent_type_slider.set(self.model.num_agent_types)
        self.agent_type_slider.pack(side=tk.LEFT, padx=5)

        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.grid(row=3, column=0, columnspan=4)

        self.reset_button = tk.Button(self.button_frame, text="Reset", command=self.reset)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        self.start_button = tk.Button(self.button_frame, text="Start", command=self.start)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.step_button = tk.Button(self.button_frame, text="Step", command=self.step)
        self.step_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(self.button_frame, text="Stop", command=self.stop)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.output_measure_button = tk.Button(self.button_frame, text="Calculate Segregation Measure", command=self.output_measure)
        self.output_measure_button.pack(side=tk.LEFT, padx=5)

    def update_canvas(self):
        self.canvas.delete("all")
        for x in range(self.model.grid_size):
            for y in range(self.model.grid_size):
                agent = self.model.grid[x, y]
                colour = COLOURS.get(agent, 'white')#defaults to white if agent not found in dictionary
                self.canvas.create_rectangle(y * self.cell_size, x * self.cell_size,
                                             (y + 1) * self.cell_size, (x + 1) * self.cell_size,
                                             fill=colour, outline="black")
        satisfaction = self.model.calculate_satisfaction()
        self.satisfaction_label.config(text=f"Satisfied Agents: {satisfaction}%")
        self.rounds_label.config(text=f"Rounds: {self.rounds}")

    def update_threshold(self, value):
        self.model.threshold = round(float(value), 2)
        self.recalculate_dissatisfaction()

    def update_empty_ratio(self, value):
        self.model.empty_ratio = round(float(value), 2)
        self.reset()

    def update_grid_size(self, value):
        grid_size = int(value)
        self.model.grid_size = grid_size
        self.cell_size = self.canvas_size / grid_size
        self.reset()

    def update_agent_types(self, value):
        num_agent_types = int(value)
        if not self.is_income_model:
            self.model = SchellingModel(grid_size=self.model.grid_size, threshold=self.model.threshold,
                                    empty_ratio=self.model.empty_ratio, num_agent_types=num_agent_types)
        else:
            self.model = SchellingIncomeModel(grid_size=self.model.grid_size, threshold=self.model.threshold,
                                    empty_ratio=self.model.empty_ratio, num_agent_types=num_agent_types,
                                    mean_income=self.model.mean_income, gini_coefficient=self.model.gini_coefficient)
        self.reset()

    def update_mean_income(self, value):
        self.model.mean_income = float(value)
        self.reset()

    def update_gini_coefficient(self, value):
        self.model.gini_coefficient = round(float(value), 2)
        self.reset()

    def reset(self):
        self.running = False
        self.rounds = 0
        self.model.grid = self.model.initialize_grid()
        self.recalculate_dissatisfaction()
        self.update_canvas()

    def start(self):
        if not self.running:
            self.running = True
            self.run_simulation()
        else:
            pass

    def stop(self):
        self.running = False

    def step(self):
        moved = self.model.step()
        if moved:
            self.rounds += 1
        self.update_canvas()

    def output_measure(self):
        composite_measure = CompositeSegregationMeasure(self.model.grid, self.model.num_agent_types, self.model.empty_ratio, self.is_income_model)
        print(f'Composite Measure: {composite_measure.calculate_composite_segregation_measure()}')

    def run_simulation(self):
        if self.running:
            moved = self.model.step()
            if moved:
                self.rounds += 1
            self.update_canvas()
            self.master.after(1, self.run_simulation)

    def recalculate_dissatisfaction(self):
        self.model.dissatisfied_agents = self.model.get_dissatisfied_agents()
