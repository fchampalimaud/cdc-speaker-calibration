import tkinter as tk
from tkinter import ttk
import matplotlib

matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class PlotFrame(ttk.Frame):
    """
    Frame responsible for displaying the Matplotlib figure in the GUI.
    """

    def __init__(self, container):
        super().__init__(container)

        # # Creates a figure
        # self.current_figure = Figure(dpi=100)

        # # Creates the FigureCanvasTkAgg object
        # self.canvas = FigureCanvasTkAgg(self.current_figure, self)

        # # Creates the toolbar
        # self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        # self.toolbar.grid(row=1, column=0, sticky="ew")

        # # Places the figure widget in the GUI
        # self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # self.grid_rowconfigure(0, weight=1)  # Allow the canvas to expand
        # self.grid_rowconfigure(0, weight=1)  # Allow the canvas to expand
        # self.grid_columnconfigure(0, weight=1)  # Allow the column to expand

        self.create_figure()

    # def set_figure(self, figure):
    #     self.canvas.get_tk_widget().destroy()
    #     self.current_figure = figure
    #     # self.canvas.figure = self.current_figure
    #     self.canvas = FigureCanvasTkAgg(self.current_figure, self)
    #     self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
    #     self.canvas.draw()

    def recreate_figure(self):
        # Destroy the existing canvas and toolbar
        self.canvas.get_tk_widget().destroy()
        self.toolbar.destroy()
        # Create a new figure
        self.create_figure()

    def create_figure(self):
        # Create a new Matplotlib figure
        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)

        # Create a canvas for the figure
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create a navigation toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Plot the initial data
        # self.plot()
