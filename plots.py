import tkinter as tk
from tkinter import Canvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import os

# Store the shaded days per month globally
shaded_days_per_month = {i: 0 for i in range(1, 13)}

def load_shaded_days(year):
    """Load the shaded days from a file for the given year."""
    global shaded_days_per_month
    directory = 'C:\\Calendar'
    file_path = os.path.join(directory, f'{year}.txt')

    shaded_days_per_month = {i: 0 for i in range(1, 13)}

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                month_idx, _ = map(int, line.strip().split(','))
                shaded_days_per_month[month_idx] += 1

def plot_shaded_days(year):
    """Plot the number of shaded days per month for the given year."""
    load_shaded_days(year)

    months = list(shaded_days_per_month.keys())
    counts = list(shaded_days_per_month.values())

    fig, ax = plt.subplots()
    ax.plot(months, counts, marker='o')
    ax.set_title(f'Shaded Days in {year}')
    ax.set_xlabel('Month')
    ax.set_ylabel('Number of Shaded Days')
    ax.set_xticks(months)
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.set_ylim(0, 31)  # Ensure y-axis range from 0 to 31
    ax.grid(False)  # Remove gridlines

    return fig

def display_plots():
    """Create and display the plot window with options to view calendar."""
    global main_window

    # Close the main window if it is open
    if 'main_window' in globals():
        main_window.destroy()

    # Initialize year with the current year
    current_year = datetime.now().year
    year_var = tk.IntVar(value=current_year)

    def update_plot(year):
        """Update the plot for the new year."""
        # Clear old plot
        for widget in plot_window.winfo_children():
            widget.destroy()

        plot_window.title(f"Shaded Days Plot for {year}")
        fig = plot_shaded_days(year)
        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Create a new Tkinter window for plots
    plot_window = tk.Tk()
    plot_window.title(f"Shaded Days Plot for {current_year}")

    # Set the window to full screen
    plot_window.attributes('-fullscreen', True)

    # Function to toggle full-screen mode
    def toggle_fullscreen(event=None):
        is_fullscreen = plot_window.attributes('-fullscreen')
        plot_window.attributes('-fullscreen', not is_fullscreen)

    # Bind the Escape key to exit full-screen mode
    plot_window.bind('<Escape>', toggle_fullscreen)

    # Initial plot
    update_plot(current_year)

    # Add a "View Calendar" button to close the plot window
    def close_window():
        plot_window.destroy()

    view_calendar_button = tk.Button(plot_window, text="View Calendar", command=close_window)
    view_calendar_button.pack(pady=10)

    # Function to toggle the button with the 'c' key
    def toggle_button(event):
        if event.keysym.lower() == 'c':
            close_window()

    # Function to handle key presses for changing the year
    def change_year(event):
        year = year_var.get()
        if event.keysym == 'Right':
            year += 1
        elif event.keysym == 'Left':
            year -= 1
        year_var.set(year)
        update_plot(year)

    # Bind keys to their respective functions
    plot_window.bind('<KeyPress-c>', toggle_button)
    plot_window.bind('<KeyPress-Right>', change_year)
    plot_window.bind('<KeyPress-Left>', change_year)

    # Run the Tkinter event loop
    plot_window.mainloop()

# Use this method to call `display_plots` from `main.py`
def set_main_window(window):
    """Set a reference to the main window."""
    global main_window
    main_window = window
