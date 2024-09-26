import matplotlib.pyplot as plt
import os
import calendar
from PIL import Image
from waveshare_epd import epd13in3k  # Import Waveshare e-paper library
from matplotlib.patches import Ellipse, Rectangle, Polygon  # Use Ellipse instead of Circle
from matplotlib.ticker import MaxNLocator  # Import MaxNLocator if needed

# We'll pass the epd object from main.py
plot_active = False  # Track whether the plot is active
first_plot = True    # Track whether it's the first time displaying the plot

# Shapes dictionary (must be consistent with main.py)
shapes = {1: "Circle", 2: "Square", 3: "Triangle"}

# ... [rest of your code remains the same] ...

# Function to draw the shapes above the plot area using fig.transFigure
def draw_shape_options(fig, current_shape):
    # Define positions and sizes in figure coordinates (0 to 1)
    shape_positions = [0.75, 0.80, 0.85]  # Positions along x-axis
    y = 0.95  # Vertical position in figure coordinates

    # Adjust the shape sizes independently to correct the aspect ratio
    shape_size_x = 0.02  # Width in figure coordinates
    # Calculate the aspect ratio correction factor
    aspect_ratio = fig.get_figheight() / fig.get_figwidth()
    shape_size_y = shape_size_x * aspect_ratio * 1.5  # Adjust multiplier as needed

    for i, x in enumerate(shape_positions):
        shape_type = i + 1  # Shape IDs start from 1
        if shape_type == 1:
            # Use Ellipse instead of Circle to adjust width and height independently
            shape = Ellipse((x, y), width=shape_size_x, height=shape_size_y, transform=fig.transFigure,
                            fill=(current_shape == 1), edgecolor='black', linewidth=1,
                            facecolor='black' if current_shape == 1 else 'white')
        elif shape_type == 2:
            shape = Rectangle((x - shape_size_x / 2, y - shape_size_y / 2),
                              shape_size_x, shape_size_y, transform=fig.transFigure,
                              fill=(current_shape == 2), edgecolor='black', linewidth=1,
                              facecolor='black' if current_shape == 2 else 'white')
        elif shape_type == 3:
            triangle = [
                [x, y + shape_size_y / 2],
                [x - shape_size_x / 2, y - shape_size_y / 2],
                [x + shape_size_x / 2, y - shape_size_y / 2]
            ]
            shape = Polygon(triangle, transform=fig.transFigure,
                            fill=(current_shape == 3), edgecolor='black', linewidth=1,
                            facecolor='black' if current_shape == 3 else 'white')
        fig.patches.append(shape)

# Function to display the plot on the e-paper display
def display_plot_on_epaper(epd, image_path):
    global first_plot
    try:
        #epd.init()  # Initialize the e-paper display

        if first_plot:
            epd.Clear()  # Clear the display only on the first plot
            print("E-paper display initialized and cleared for the first plot.")
        else:
            print("E-paper display initialized for plot update.")

        # Ensure the image matches the e-paper's dimensions
        image = Image.open(image_path)
        image = image.convert('1')  # Convert image to 1-bit color

        # Resize the image to fit the e-paper display if necessary
        epd_width = epd.width
        epd_height = epd.height
        image = image.resize((epd_width, epd_height), Image.ANTIALIAS)

        epd.display(epd.getbuffer(image))  # Send the image buffer to the display
        print("Plot displayed on the e-paper.")
    except Exception as e:
        print(f"Error displaying plot on e-paper: {e}")

# Function to close the plot
def close_plot(epd):
    global plot_active, first_plot
    try:
        plot_active = False
        first_plot = True  # Reset first_plot flag for next time
        print("Plot closed.")
    except Exception as e:
        print(f"Error closing plot: {e}")
        plot_active = False
        first_plot = True  # Ensure flag is reset even on error
