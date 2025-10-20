from ipywidgets import Dropdown, VBox, Output
from IPython.display import display
import plotly.graph_objects as go
import math

class EpistemicSpace:
    def __init__(self, n_props, proposition_texts=None):
        self.n_props = n_props
        self.n_possibilities = 2 ** n_props
        if proposition_texts is not None:
            if len(proposition_texts) != n_props:
                raise ValueError("Length of proposition_texts must match n_props")
            self.proposition_texts = proposition_texts
        else:
            self.proposition_texts = [f"B{i+1}" for i in range(n_props)]

    def get_possibility_bitstring(self, i):
        return format(i, f'0{self.n_props}b')

    def get_set_theory_notation(self, i, use_text=True):
        bitstring = self.get_possibility_bitstring(i)
        terms = []
        for j, bit in enumerate(bitstring):
            prop = self.proposition_texts[j] if use_text else f"B{j+1}"
            terms.append(prop if bit == "1" else f"¬{prop}")
        return " ∩ ".join(terms)

    def visualize_interactive(self, use_text=True):
        """Interactive Plotly visualization that highlights selected proposition."""

        n = self.n_possibilities
        grid_cols = math.ceil(math.sqrt(n))
        grid_rows = math.ceil(n / grid_cols)
        marker_size = 10

        # Compute coordinates
        x, y = [], []
        for i in range(n):
            row = i // grid_cols
            col = i % grid_cols
            x.append(col)
            y.append(row)

        # Precompute hover text
        hover_text = []
        for i in range(n):
            bitstring = self.get_possibility_bitstring(i)
            symbolic = []
            sentences = []
            for j, bit in enumerate(bitstring):
                p = self.proposition_texts[j]
                symbolic.append(f"B{j+1}" if bit == "1" else f"¬B{j+1}")
                sentences.append(p if bit == "1" else f"¬{p}")
            hover_text.append(f"{' ∩ '.join(symbolic)}<br>{' ∩<br>'.join(sentences)}")

        # Base figure
        fig = go.FigureWidget(
            data=[go.Scatter(
                x=x,
                y=y,
                mode='markers+text',
                marker=dict(size=marker_size, color='lightblue', line=dict(width=1, color='darkblue')),
                text=[self.get_possibility_bitstring(i) for i in range(n)],
                textposition="bottom center",
                hovertext=hover_text,
                hovertemplate="%{hovertext}<extra></extra>"
            )]
        )

        fig.update_layout(
            title=f"Epistemic Space ({self.n_props} propositions, {n} possibilities)",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="y"),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, autorange='reversed'),
            width=600,
            height=600,
        )

        # Dropdown to choose proposition
        dropdown = Dropdown(
            options=["None"] + [f"B{i+1}" for i in range(self.n_props)],
            value="None",
            description="Highlight:"
        )

        out = Output()

        def update_highlight(change):
            with out:
                out.clear_output(wait=True)
                prop = change["new"]
                if prop == "None":
                    fig.data[0].marker.color = ['lightblue'] * n
                else:
                    idx = int(prop[1:]) - 1
                    colors = []
                    for i in range(n):
                        bit = self.get_possibility_bitstring(i)[idx]
                        colors.append("gold" if bit == "1" else "lightgray")
                    fig.data[0].marker.color = colors

        dropdown.observe(update_highlight, names="value")

        display(VBox([dropdown, fig, out]))

        # Initial state
        update_highlight({"new": "None"})

