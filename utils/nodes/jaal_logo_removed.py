import dash
import dash_bootstrap_components as dbc
import pandas as pd
import visdcc
from dash import html
from dash.dependencies import Input, Output, State
from jaal import Jaal
from screeninfo import get_monitors

# Constants
# --------------
# default node and edge size
DEFAULT_NODE_SIZE = 7
DEFAULT_EDGE_SIZE = 1

# default node and egde color
DEFAULT_COLOR = "#97C2FC"

# Taken from https://stackoverflow.com/questions/470690/how-to-automatically-generate-n-distinct-colors
KELLY_COLORS_HEX = [
    "#FFB300",  # Vivid Yellow
    "#803E75",  # Strong Purple
    "#FF6800",  # Vivid Orange
    "#A6BDD7",  # Very Light Blue
    "#C10020",  # Vivid Red
    "#CEA262",  # Grayish Yellow
    "#817066",  # Medium Gray
    # The following don't work well for people with defective color vision
    "#007D34",  # Vivid Green
    "#F6768E",  # Strong Purplish Pink
    "#00538A",  # Strong Blue
    "#FF7A5C",  # Strong Yellowish Pink
    "#53377A",  # Strong Violet
    "#FF8E00",  # Vivid Orange Yellow
    "#B32851",  # Strong Purplish Red
    "#F4C800",  # Vivid Greenish Yellow
    "#7F180D",  # Strong Reddish Brown
    "#93AA00",  # Vivid Yellowish Green
    "#593315",  # Deep Yellowish Brown
    "#F13A13",  # Vivid Reddish Orange
    "#232C16",  # Dark Olive Green
]

DEFAULT_OPTIONS = {
    "height": f"{get_monitors()[0].height}px",
    "width": "100%",
    "interaction": {"hover": True},
    # 'edges': {'scaling': {'min': 1, 'max': 5}},
    "physics": {"stabilization": {"iterations": 100}},
}

# Code
# ---------
def get_options(directed, opts_args):
    opts = DEFAULT_OPTIONS.copy()
    opts["edges"] = {"arrows": {"to": directed}}
    if opts_args is not None:
        opts.update(opts_args)
    return opts


def get_distinct_colors(n):
    """Return distict colors, currently atmost 20

    Parameters
    -----------
    n: int
        the distinct colors required
    """
    if n <= 20:
        return KELLY_COLORS_HEX[:n]


def create_card(id, value, description):
    """Creates card for high level stats

    Parameters
    ---------------
    """
    return dbc.Card(
        dbc.CardBody(
            [
                html.H4(id=id, children=value, className="card-title"),
                html.P(children=description),
            ]
        )
    )


def create_color_legend(text, color):
    """Individual row for the color legend"""
    return create_row(
        [
            html.Div(style={"width": "10px", "height": "10px", "background-color": color}),
            html.Div(text, style={"padding-left": "10px"}),
        ]
    )


def fetch_flex_row_style():
    return {"display": "flex", "flex-direction": "row", "justify-content": "center", "align-items": "center"}


def create_row(children, style=fetch_flex_row_style()):
    return dbc.Row(children, style=style, className="column flex-display")


search_form = dbc.FormGroup(
    [
        # dbc.Label("Search", html_for="search_graph"),
        dbc.Input(type="search", id="search_graph", placeholder="Search node in graph..."),
        dbc.FormText(
            "Show the node you are looking for",
            color="secondary",
        ),
    ]
)

filter_node_form = dbc.FormGroup(
    [
        # dbc.Label("Filter nodes", html_for="filter_nodes"),
        dbc.Textarea(id="filter_nodes", placeholder="Enter filter node query here..."),
        dbc.FormText(
            html.P(
                [
                    "Filter on nodes properties by using ",
                    html.A(
                        "Pandas Query syntax",
                        href="https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html",
                    ),
                ]
            ),
            color="secondary",
        ),
    ]
)

filter_edge_form = dbc.FormGroup(
    [
        # dbc.Label("Filter edges", html_for="filter_edges"),
        dbc.Textarea(id="filter_edges", placeholder="Enter filter edge query here..."),
        dbc.FormText(
            html.P(
                [
                    "Filter on edges properties by using ",
                    html.A(
                        "Pandas Query syntax",
                        href="https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html",
                    ),
                ]
            ),
            color="secondary",
        ),
    ]
)


def get_select_form_layout(id, options, label, description):
    """Creates a select (dropdown) form with provides details

    Parameters
    -----------
    id: str
        id of the form
    options: list
        options to show
    label: str
        label of the select dropdown bar
    description: str
        long text detail of the setting
    """
    return dbc.FormGroup(
        [
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon(label, addon_type="append"),
                    dbc.Select(id=id, options=options),
                ]
            ),
            dbc.FormText(
                description,
                color="secondary",
            ),
        ]
    )


def get_categorical_features(df_, unique_limit=20, blacklist_features=["shape", "label", "id"]):
    """Identify categorical features for edge or node data and return their names
    Additional logics: (1) cardinality should be within `unique_limit`, (2) remove blacklist_features
    """
    # identify the rel cols + None
    cat_features = ["None"] + df_.columns[
        (df_.dtypes == "object") & (df_.apply(pd.Series.nunique) <= unique_limit)
    ].tolist()
    # remove irrelevant cols
    try:
        for col in blacklist_features:
            cat_features.remove(col)
    except:
        pass
    # return
    return cat_features


def get_numerical_features(df_, unique_limit=20):
    """Identify numerical features for edge or node data and return their names"""
    # supported numerical cols
    numerics = ["int16", "int32", "int64", "float16", "float32", "float64"]
    # identify numerical features
    numeric_features = ["None"] + df_.select_dtypes(include=numerics).columns.tolist()
    # remove blacklist cols (for nodes)
    try:
        numeric_features.remove("size")
    except:
        pass
    # return
    return numeric_features


class JaalLogoRemoved(Jaal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create(self, directed=False, vis_opts=None):
        """Create the Jaal app and return it

        Parameter
        ----------
            directed: boolean
                process the graph as directed graph?

            vis_opts: dict
                the visual options to be passed to the dash server (default: None)

        Returns
        -------
            app: dash.Dash
                the Jaal app
        """
        # create the app
        app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

        # define layout
        app.layout = self.get_app_layout(
            self.data, color_legends=self.get_color_popover_legend_children(), directed=directed, vis_opts=vis_opts
        )

        # create callbacks to toggle legend popover
        @app.callback(
            Output("color-legend-popup", "is_open"),
            [Input("color-legend-toggle", "n_clicks")],
            [State("color-legend-popup", "is_open")],
        )
        def toggle_popover(n, is_open):
            if n:
                return not is_open
            return is_open

        # create callbacks to toggle hide/show sections - FILTER section
        @app.callback(
            Output("filter-show-toggle", "is_open"),
            [Input("filter-show-toggle-button", "n_clicks")],
            [State("filter-show-toggle", "is_open")],
        )
        def toggle_filter_collapse(n, is_open):
            if n:
                return not is_open
            return is_open

        # create callbacks to toggle hide/show sections - COLOR section
        @app.callback(
            Output("color-show-toggle", "is_open"),
            [Input("color-show-toggle-button", "n_clicks")],
            [State("color-show-toggle", "is_open")],
        )
        def toggle_filter_collapse(n, is_open):
            if n:
                return not is_open
            return is_open

        # create callbacks to toggle hide/show sections - COLOR section
        @app.callback(
            Output("size-show-toggle", "is_open"),
            [Input("size-show-toggle-button", "n_clicks")],
            [State("size-show-toggle", "is_open")],
        )
        def toggle_filter_collapse(n, is_open):
            if n:
                return not is_open
            return is_open

        # create the main callbacks
        @app.callback(
            [Output("graph", "data"), Output("color-legend-popup", "children")],
            [
                Input("search_graph", "value"),
                Input("filter_nodes", "value"),
                Input("filter_edges", "value"),
                Input("color_nodes", "value"),
                Input("color_edges", "value"),
                Input("size_nodes", "value"),
                Input("size_edges", "value"),
            ],
            [State("graph", "data")],
        )
        def setting_pane_callback(
            search_text,
            filter_nodes_text,
            filter_edges_text,
            color_nodes_value,
            color_edges_value,
            size_nodes_value,
            size_edges_value,
            graph_data,
        ):
            # fetch the id of option which triggered
            ctx = dash.callback_context
            # if its the first call
            if not ctx.triggered:
                print("No trigger")
                return [self.data, self.get_color_popover_legend_children()]
            else:
                # find the id of the option which was triggered
                input_id = ctx.triggered[0]["prop_id"].split(".")[0]
                # perform operation in case of search graph option
                if input_id == "search_graph":
                    graph_data = self._callback_search_graph(graph_data, search_text)
                # In case filter nodes was triggered
                elif input_id == "filter_nodes":
                    graph_data = self._callback_filter_nodes(graph_data, filter_nodes_text)
                # In case filter edges was triggered
                elif input_id == "filter_edges":
                    graph_data = self._callback_filter_edges(graph_data, filter_edges_text)
                # If color node text is provided
                if input_id == "color_nodes":
                    graph_data, self.node_value_color_mapping = self._callback_color_nodes(
                        graph_data, color_nodes_value
                    )
                # If color edge text is provided
                if input_id == "color_edges":
                    graph_data, self.edge_value_color_mapping = self._callback_color_edges(
                        graph_data, color_edges_value
                    )
                # If size node text is provided
                if input_id == "size_nodes":
                    graph_data = self._callback_size_nodes(graph_data, size_nodes_value)
                # If size edge text is provided
                if input_id == "size_edges":
                    graph_data = self._callback_size_edges(graph_data, size_edges_value)
            # create the color legend childrens
            color_popover_legend_children = self.get_color_popover_legend_children(
                self.node_value_color_mapping, self.edge_value_color_mapping
            )
            # finally return the modified data
            return [graph_data, color_popover_legend_children]

        # return server
        return app

    def get_app_layout(self, graph_data, color_legends=[], directed=False, vis_opts=None):
        """Create and return the layout of the app

        Parameters
        --------------
        graph_data: dict{nodes, edges}
            network data in format of visdcc
        """

        # Step 1-2: find categorical features of nodes and edges
        cat_node_features = get_categorical_features(pd.DataFrame(graph_data["nodes"]), 20, ["shape", "label", "id"])
        cat_edge_features = get_categorical_features(
            pd.DataFrame(graph_data["edges"]).drop(columns=["color"]), 20, ["color", "from", "to", "id"]
        )
        # Step 3-4: Get numerical features of nodes and edges
        num_node_features = get_numerical_features(pd.DataFrame(graph_data["nodes"]))
        num_edge_features = get_numerical_features(pd.DataFrame(graph_data["edges"]))
        # Step 5: create and return the layout
        # resolve path
        return html.Div(
            [
                # create_row(html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), width="80px")),
                create_row(
                    [
                        dbc.Col(
                            [
                                # setting panel
                                dbc.Form(
                                    [
                                        # ---- search section ----
                                        html.H6("Search"),
                                        html.Hr(className="my-2"),
                                        search_form,
                                        # ---- filter section ----
                                        create_row(
                                            [
                                                html.H6("Filter"),
                                                dbc.Button(
                                                    "Hide/Show",
                                                    id="filter-show-toggle-button",
                                                    outline=True,
                                                    color="secondary",
                                                    size="sm",
                                                ),  # legend
                                            ],
                                            {
                                                **fetch_flex_row_style(),
                                                "margin-left": 0,
                                                "margin-right": 0,
                                                "justify-content": "space-between",
                                            },
                                        ),
                                        dbc.Collapse(
                                            [
                                                html.Hr(className="my-2"),
                                                filter_node_form,
                                                filter_edge_form,
                                            ],
                                            id="filter-show-toggle",
                                            is_open=False,
                                        ),
                                        # ---- color section ----
                                        create_row(
                                            [
                                                html.H6("Color"),  # heading
                                                html.Div(
                                                    [
                                                        dbc.Button(
                                                            "Hide/Show",
                                                            id="color-show-toggle-button",
                                                            outline=True,
                                                            color="secondary",
                                                            size="sm",
                                                        ),  # legend
                                                        dbc.Button(
                                                            "Legends",
                                                            id="color-legend-toggle",
                                                            outline=True,
                                                            color="secondary",
                                                            size="sm",
                                                        ),  # legend
                                                    ]
                                                ),
                                                # add the legends popup
                                                dbc.Popover(
                                                    children=color_legends,
                                                    id="color-legend-popup",
                                                    is_open=False,
                                                    target="color-legend-toggle",
                                                ),
                                            ],
                                            {
                                                **fetch_flex_row_style(),
                                                "margin-left": 0,
                                                "margin-right": 0,
                                                "justify-content": "space-between",
                                            },
                                        ),
                                        dbc.Collapse(
                                            [
                                                html.Hr(className="my-2"),
                                                get_select_form_layout(
                                                    id="color_nodes",
                                                    options=[{"label": opt, "value": opt} for opt in cat_node_features],
                                                    label="Color nodes by",
                                                    description="Select the categorical node property to color nodes by",
                                                ),
                                                get_select_form_layout(
                                                    id="color_edges",
                                                    options=[{"label": opt, "value": opt} for opt in cat_edge_features],
                                                    label="Color edges by",
                                                    description="Select the categorical edge property to color edges by",
                                                ),
                                            ],
                                            id="color-show-toggle",
                                            is_open=True,
                                        ),
                                        # ---- size section ----
                                        create_row(
                                            [
                                                html.H6("Size"),  # heading
                                                dbc.Button(
                                                    "Hide/Show",
                                                    id="size-show-toggle-button",
                                                    outline=True,
                                                    color="secondary",
                                                    size="sm",
                                                ),  # legend
                                                # dbc.Button("Legends", id="color-legend-toggle", outline=True, color="secondary", size="sm"), # legend
                                                # add the legends popup
                                                # dbc.Popover(
                                                #     children=color_legends,
                                                #     id="color-legend-popup", is_open=False, target="color-legend-toggle",
                                                # ),
                                            ],
                                            {
                                                **fetch_flex_row_style(),
                                                "margin-left": 0,
                                                "margin-right": 0,
                                                "justify-content": "space-between",
                                            },
                                        ),
                                        dbc.Collapse(
                                            [
                                                html.Hr(className="my-2"),
                                                get_select_form_layout(
                                                    id="size_nodes",
                                                    options=[{"label": opt, "value": opt} for opt in num_node_features],
                                                    label="Size nodes by",
                                                    description="Select the numerical node property to size nodes by",
                                                ),
                                                get_select_form_layout(
                                                    id="size_edges",
                                                    options=[{"label": opt, "value": opt} for opt in num_edge_features],
                                                    label="Size edges by",
                                                    description="Select the numerical edge property to size edges by",
                                                ),
                                            ],
                                            id="size-show-toggle",
                                            is_open=True,
                                        ),
                                    ],
                                    className="card",
                                    style={"padding": "5px", "background": "#e5e5e5"},
                                ),
                            ],
                            width=3,
                            style={"display": "flex", "justify-content": "center", "align-items": "center"},
                        ),
                        # graph
                        dbc.Col(
                            visdcc.Network(id="graph", data=graph_data, options=get_options(directed, vis_opts)),
                            width=9,
                        ),
                    ]
                ),
            ]
        )
