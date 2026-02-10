# Extended Schelling Model of Segregation

## Project Structure

```
schelling_project/
├── main.py                          # Entry point - run this to start the application
├── models/
│   ├── __init__.py
│   ├── schelling_model.py           # Base Schelling model
│   └── schelling_income_model.py    # Extended model with income groups
├── measures/
│   ├── __init__.py
│   └── composite_segregation_measure.py  # Segregation metrics calculations
├── gui/
│   ├── __init__.py
│   ├── schelling_app.py             # Individual tab GUI
│   └── main_app.py                  # Main application with tabs
└── utils/
    ├── __init__.py
    └── constants.py                 # Color definitions for agents

```

## How to Run

```bash
python main.py
```

## File Descriptions

- **main.py**: The entry point that creates the tkinter window and starts the application
- **models/schelling_model.py**: Contains the base Schelling model with grid initialization, satisfaction calculation, and agent movement logic
- **models/schelling_income_model.py**: Extends the base model to include income groups with Gini coefficient distributions
- **measures/composite_segregation_measure.py**: Calculates segregation metrics including isolation index, Moran's I, and dissimilarity index
- **gui/schelling_app.py**: Creates the GUI for a single model (canvas, controls, buttons)
- **gui/main_app.py**: Manages the tabbed interface for switching between different models
- **utils/constants.py**: Defines color schemes for different agent types and income groups

## Notes

All functionality remains exactly the same as the original single-file implementation. The code has simply been reorganized into logical modules for better maintainability.
