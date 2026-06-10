from fasthtml.common import fast_app, serve, H1, Div
import matplotlib.pyplot as plt
from combined_components import FormGroup, CombinedComponent

# Ensure project root is importable when running this file as a script
import os
import sys
from pathlib import Path

# Import QueryBase, Employee, Team from employee_events
from employee_events import QueryBase, Employee, Team

# Add the project root (parent of the `report` package) to sys.path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# import the load_model function from the utils.py file
from report.utils import load_model

"""
Below, we import the parent classes
you will use for subclassing
"""
from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable
)


# Create a subclass of base_components/dropdown
# called `ReportDropdown`
class ReportDropdown(Dropdown):

    # Set the `label` attribute so it is set
    # to the `name` attribute for the model
    def __init__(self, id="selector", name="user-selection", label=""):
        super().__init__(id=id, name=name, label=label)

    # Return the output from the
    # parent class's build_component method
    def build_component(self, entity_id, model):
        self.label = model.name.title() if getattr(model, 'name', None) else self.label
        return super().build_component(entity_id, model)

    # Overwrite the `component_data` method
    # Ensure the method uses the same parameters
    # as the parent class method

    def component_data(self, entity_id, model):
        # Using the model argument
        # call the employee_events method
        # that returns the user-type's
        # names and ids
        return model.names()


# Create a subclass of base_components/BaseComponent
# called `Header`
class Header(BaseComponent):

    # Overwrite the `build_component` method
    # Ensure the method has the same parameters
    # as the parent class
    def build_component(self, entity_id, model):

        # Using the model argument for this method
        # return a fasthtml H1 objects
        # containing the model's name attribute
        title = getattr(model, 'name', '')
        return H1(title.title() if title else '')

# Create a subclass of base_components/MatplotlibViz
# called `LineChart`
#### YOUR CODE HERE


class LineChart(MatplotlibViz):
    # Overwrite the parent class's `visualization`
    # method. Use the same parameters as the parent
    #### YOUR CODE HERE
    def visualization(self, asset_id, model):
        # Pass the `asset_id` argument to
        # the model's `event_counts` method to
        # receive the x (Day) and y (event count)
        df = model.event_counts(asset_id)
        # Use the pandas .fillna method to fill nulls with 0
        df = df.fillna(0)
        # User the pandas .set_index method to set
        # the date column as the index
        df = df.set_index('event_date')
        # Sort the index
        df = df.sort_index()
        # Use the .cumsum method to change the data
        # in the dataframe to cumulative counts
        df = df.cumsum()
        # Set the dataframe columns to the list
        # ['Positive', 'Negative']
        df.columns = ['Positive', 'Negative']
        # Initialize a pandas subplot
        # and assign the figure and axis
        # to variables
        fig, ax = plt.subplots()
        # call the .plot method for the
        # cumulative counts dataframe
        df.plot(ax=ax)
        # pass the axis variable
        # to the `.set_axis_styling`
        # method
        # Use keyword arguments to set
        # the border color and font color to black.
        # Reference the base_components/matplotlib_viz file
        # to inspect the supported keyword arguments
        self.set_axis_styling(ax, bordercolor='black', fontcolor='black')

        # Set title and labels for x and y axis
        ax.set_title('Cumulative Events', fontsize=14)
        ax.set_xlabel('Date')
        ax.set_ylabel('Cumulative Count')


# Create a subclass of base_components/MatplotlibViz
# called `BarChart`
#### YOUR CODE HERE
class BarChart(MatplotlibViz):
    # Create a `predictor` class attribute
    # assign the attribute to the output
    # of the `load_model` utils function
    #### YOUR CODE HERE
    # Defer loading the ML model until visualization is actually called
    # to avoid importing heavy packages at module import time.
    predictor = None

    # Overwrite the parent class `visualization` method
    # Use the same parameters as the parent
    #### YOUR CODE HERE
    def visualization(self, asset_id, model):
        # Lazy-load the predictor if it hasn't been loaded yet
        if self.predictor is None:
            self.predictor = load_model()
        # Using the model and asset_id arguments
        # pass the `asset_id` to the `.model_data` method
        # to receive the data that can be passed to the machine
        # learning model
        data = model.model_data(asset_id)
        # Using the predictor class attribute
        # pass the data to the `predict_proba` method
        probs = self.predictor.predict_proba(data)
        # Index the second column of predict_proba output
        # The shape should be (<number of records>, 1)
        try:
            probs = probs[:, 1]
        except Exception:
            probs = probs.ravel()
        # Below, create a `pred` variable set to
        # the number we want to visualize
        #
        # If the model's name attribute is "team"
        # We want to visualize the mean of the predict_proba output
        if getattr(model, 'name', '') == 'team':
            pred = float(probs.mean())
        else:
            pred = float(probs[0]) if len(probs) > 0 else 0.0

        # Initialize a matplotlib subplot
        fig, ax = plt.subplots()

        # Otherwise set `pred` to the first value
        # of the predict_proba output

        # Run the following code unchanged
        ax.barh([''], [pred])
        ax.set_xlim(0, 1)
        ax.set_title('Predicted Recruitment Risk', fontsize=20)
        # pass the axis variable
        # to the `.set_axis_styling`
        # method
        self.set_axis_styling(ax, bordercolor='black', fontcolor='black')

# Create a subclass of combined_components/CombinedComponent
# called Visualizations
#### YOUR CODE HERE


class Visualizations(CombinedComponent):
    # Set the `children`
    # class attribute to a list
    # containing an initialized
    # instance of `LineChart` and `BarChart`
    #### YOUR CODE HERE
    children = [LineChart(), BarChart()]

    # Leave this line unchanged
    outer_div_type = Div(cls='grid')

# Create a subclass of base_components/DataTable
# called `NotesTable`
#### YOUR CODE HERE


class NotesTable(DataTable):
    # Overwrite the `component_data` method
    # using the same parameters as the parent class
    #### YOUR CODE HERE
    def component_data(self, entity_id, model):
        # Using the model and entity_id arguments
        # pass the entity_id to the model's .notes
        # method. Return the output
        return model.notes(entity_id)


class DashboardFilters(FormGroup):

    id = "top-filters"
    action = "/update_data"
    method = "POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector'
        ),
        ReportDropdown(
            id="selector",
            name="user-selection")
    ]


# Create a subclass of CombinedComponents
# called `Report`
class Report(CombinedComponent):
    # Set the `children`
    # class attribute to a list
    # containing initialized instances
    # of the header, dashboard filters,
    # data visualizations, and notes table
    #### YOUR CODE HERE
    children = [Header(), DashboardFilters(), Visualizations(), NotesTable()]

    # Set the `children`
    # class attribute to a list
    # containing initialized instances
    # of the header, dashboard filters,
    # data visualizations, and notes table
    #### YOUR CODE HERE


# Initialize a fasthtml app
app, rt = fast_app()

# Initialize the `Report` class
#### YOUR CODE HERE
report = Report()


# Create a route for a get request
# Set the route's path to the root
#### YOUR CODE HERE
@app.get('/')
def index(r):
    # Call the initialized report
    # pass the integer 1 and an instance
    # of the Employee class as arguments
    # Return the result
    return report(1, Employee())

    # Call the initialized report
    # pass the integer 1 and an instance
    # of the Employee class as arguments
    # Return the result
    #### YOUR CODE HERE

# Create a route for a get request
# Set the route's path to receive a request
# for an employee ID so `/employee/2`
# will return the page for the employee with
# an ID of `2`.
# parameterize the employee ID
# to a string datatype


@app.get('/employee/{id}')
def employee_route(r, id: str):
    # Call the initialized report
    # pass the ID and an instance
    # of the Employee SQL class as arguments
    # Return the result
    return report(id, Employee())

    # Call the initialized report
    # pass the ID and an instance
    # of the Employee SQL class as arguments
    # Return the result
    #### YOUR CODE HERE

# Create a route for a get request
# Set the route's path to receive a request
# for a team ID so `/team/2`
# will return the page for the team with
# an ID of `2`.
# parameterize the team ID
# to a string datatype
#### YOUR CODE HERE


@app.get('/team/{id}')
def team_route(r, id: str):
    # Call the initialized report
    # pass the id and an instance
    # of the Team SQL class as arguments
    # Return the result
    return report(id, Team())

    # Call the initialized report
    # pass the id and an instance
    # of the Team SQL class as arguments
    # Return the result
    #### YOUR CODE HERE


# Keep the below code unchanged!
@app.get('/update_dropdown{r}')
def update_dropdown(r):
    dropdown = DashboardFilters.children[1]
    print('PARAM', r.query_params['profile_type'])
    if r.query_params['profile_type'] == 'Team':
        return dropdown(None, Team())
    elif r.query_params['profile_type'] == 'Employee':
        return dropdown(None, Employee())


@app.post('/update_data')
async def update_data(r):
    from fasthtml.common import RedirectResponse
    data = await r.form()
    profile_type = data._dict['profile_type']
    id = data._dict['user-selection']
    if profile_type == 'Employee':
        return RedirectResponse(f"/employee/{id}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{id}", status_code=303)


serve()
