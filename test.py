# import tkinter as tk
# from tkinter import ttk
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import matplotlib.pyplot as plt
# import numpy as np


# class App:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Matplotlib in Tkinter")

#         # Create a frame for the Matplotlib figure
#         self.figure_frame = ttk.Frame(self.root, width=500, height=400)
#         self.figure_frame.pack(fill=tk.BOTH, expand=True)

#         # Create two figures
#         self.fig1 = self.create_figure1()
#         self.fig2 = self.create_figure2()

#         # Initially, no figure is displayed
#         self.current_figure = None
#         self.canvas = None

#         # Create a button to show the first figure
#         self.show_button = ttk.Button(
#             self.root, text="Show Figure", command=self.show_figure
#         )
#         self.show_button.pack()

#         # Create a button to switch figures
#         self.switch_button = ttk.Button(
#             self.root, text="Switch Figure", command=self.switch_figure
#         )
#         self.switch_button.pack()
#         self.switch_button.config(state=tk.DISABLED)  # Disable switch button initially

#     def create_figure1(self):
#         fig = plt.Figure(figsize=(5, 4), dpi=100)
#         ax = fig.add_subplot(111)
#         x = np.linspace(0, 10, 100)
#         y = np.sin(x)
#         ax.plot(x, y)
#         ax.set_title("Figure 1: Sine Wave")
#         return fig

#     def create_figure2(self):
#         fig = plt.Figure(figsize=(5, 4), dpi=100)
#         ax = fig.add_subplot(111)
#         x = np.linspace(0, 10, 100)
#         y = np.cos(x)
#         ax.plot(x, y)
#         ax.set_title("Figure 2: Cosine Wave")
#         return fig

#     def show_figure(self):
#         # Show the first figure on the first button press
#         if self.current_figure is None:
#             self.current_figure = self.fig1
#             self.canvas = FigureCanvasTkAgg(
#                 self.current_figure, master=self.figure_frame
#             )
#             self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
#             self.canvas.draw()
#             self.switch_button.config(state=tk.NORMAL)  # Enable switch button

#     def switch_figure(self):
#         # Clear the current figure
#         self.canvas.get_tk_widget().destroy()

#         # Switch the figure
#         if self.current_figure == self.fig1:
#             self.current_figure = self.fig2
#         else:
#             self.current_figure = self.fig1

#         # Create a new canvas for the new figure
#         self.canvas = FigureCanvasTkAgg(self.current_figure, master=self.figure_frame)
#         self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
#         self.canvas.draw()


# if __name__ == "__main__":
#     root = tk.Tk()
#     app = App(root)
#     root.mainloop()

# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.widgets import Button

# # Create initial data
# data = np.random.rand(10, 10)

# # Create the initial imshow plot
# fig, ax = plt.subplots()
# img = ax.imshow(data, cmap='plasma')
# plt.colorbar(img)

# # Function to update the data
# def update_data(event):
#     new_data = np.random.rand(10, 10)  # Generate new random data
#     img.set_data(new_data)              # Update the data of the imshow
#     plt.draw()                          # Redraw the figure

# # Create a button
# ax_button = plt.axes([0.8, 0.01, 0.1, 0.05])  # Position of the button
# button = Button(ax_button, 'Update')

# # Connect the button to the update function
# button.on_clicked(update_data)

# # Show the plot
# plt.show()

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

# Create initial data
data = np.random.rand(10, 10)

# Create the initial imshow plot
fig, ax = plt.subplots()
img = ax.imshow(data, cmap='viridis')
plt.colorbar(img)

# Function to update the data with a new size
def update_data(event):
    new_size = np.random.randint(5, 15)  # Random new size between 5 and 15
    new_data = np.random.rand(new_size, new_size)  # Generate new random data
    ax.clear()  # Clear the current axes
    img = ax.imshow(new_data, cmap='viridis')  # Create a new imshow with the new data
    # plt.colorbar(img)  # Add a colorbar
    plt.draw()  # Redraw the figure

# Create a button
ax_button = plt.axes([0.8, 0.01, 0.1, 0.05])  # Position of the button
button = Button(ax_button, 'Update Size')

# Connect the button to the update function
button.on_clicked(update_data)

# Show the plot
plt.show()
