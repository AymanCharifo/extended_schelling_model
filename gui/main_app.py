import tkinter as tk
from tkinter import ttk
from models import SchellingModel, SchellingIncomeModel
from .schelling_app import SchellingApp


class MainApp:
    def __init__(self, root):
        self.root = root
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")
        self.tabs = []

        #tab1
        tab1 = ttk.Frame(self.notebook)
        self.notebook.add(tab1, text="Schelling Model")
        model1 = SchellingModel(grid_size=50, threshold=0.3)
        app1 = SchellingApp(tab1, model1)
        self.tabs.append(app1)

        #tab2
        tab2 = ttk.Frame(self.notebook)
        self.notebook.add(tab2, text="Two-Attribute Schelling Model")
        model2 = SchellingIncomeModel(grid_size=50, threshold=0.3, mean_income=40000)
        app2 = SchellingApp(tab2, model2, is_income_model=True)
        self.tabs.append(app2)

        self.current_app = self.tabs[0]#default model is app1

        #bind tab to change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        selected_tab_index = self.notebook.index(self.notebook.select())#new tab index
        
        if self.current_app.running:  
            self.current_app.stop() 
        
        self.current_app = self.tabs[selected_tab_index]#updates current app
