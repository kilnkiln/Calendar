import matplotlib.pyplot as plt
import os
import calendar
from PIL import Image
from waveshare_epd import epd13in3k  # Import Waveshare e-paper library
from matplotlib.patches import Ellipse, Rectangle, Polygon
from matplotlib.ticker import MaxNLocator  # Import MaxNLocator if needed

# We'll pass the epd object from main.py
plot_active = False  # Track whether the plot is active
first_plot = True    # Track whether it's the first time displaying the plot

# Shapes dictionary (must be consistent with main.py)
shapes = {1: "Circle", 2: "Square", 3: "Triangle"}

# Function to read the shaded days from the txt file for the selected year and shape
def read_shaded_days(year, shape):
    data_dir = '/home/admin/CalendarDatabase'
    file_path = os.path.join(data_dir, f'{year}.txt')
    if not os.path.exists(file_path):
        print(f"No data for {year}.")
        return {}
    
    shaded_days = {}
    with open(file_path, 'r') as file:
        for line in file:
            values = line.strip().split(',')
            if len(values) >= 3:
                month, day, shape_type = map(int, values[:3])
                if shape_type == shape:
                    if month not in shaded_days:
                        shaded_days[month] = []
                    shaded_days[month].append(day)
            else:
                continue  # Skip lines that don't have enough data
    return shaded_days

# Function to generate the plot as a PNG image and display it on the e-paper
def plot_year_data(epd, year, shape):
    global plot_active, shapes, first_plot  # Ensure variables are in scope

    shaded_days = read_shaded_days(year, shape)
    if not shaded_days:
        print("No shaded days found for the selected shape.")
        # Skip clearing the e-paper display
        return

    # Prepare data for plotting
    months = list(range(1, 13))
    days_count = [len(shaded_days.get(month, [])) for month in months]

    # Adjust the figure size and DPI to match e-paper resolution (960x680)
    dpi = 100  # Adjust DPI if necessary
    fig_width = 960 / dpi  # 9.6 inches
    fig_height = 680 / dpi  # 6.8 inches

    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')  # Ensure background is white

    # Adjust the plot area to leave room at the top
    plt.subplots_adjust(top=0.85)  # Leave space at the top for the title and shapes

    # Set title
    fig.suptitle(f'{shapes[shape]} Shaded Days in {year}', fontsize=24, color='black', y=0.96)

    # Draw shapes above the plot area, inline with the title
    draw_shape_options(fig, shape)

    # Plot the data as a line plot
    ax.plot(months, days_count, color='black', marker='o')

    # Add data labels above each point
    for x, y in zip(months, days_count):
        ax.text(x, y + 0.5, str(y), ha='center', va='bottom', fontsize=12)

    # Set x-axis to months with abbreviations
    ax.set_xticks(months)
    ax.set_xticklabels([calendar.month_abbr[m] for m in months], fontsize=16)

    # Set y-axis from 1 to 31
    ax.set_ylim(1, 31)
    ax.set_yticks(range(1, 32))

    # Adjust y-axis label font size
    ax.tick_params(axis='y', which='major', labelsize=12)
    ax.tick_params(axis='x', which='major', labelsize=16)

    # Remove axis labels
    ax.set_xlabel('')
    ax.set_ylabel('')

    # Remove extra whitespace
    plt.tight_layout()

    # Save the plot as a .png image to display on the e-paper
    plot_file = '/tmp/plot.png'
    fig.savefig(plot_file, format='png', facecolor='white')
    plt.close(fig)  # Close the figure after saving

    # Load the image and display on the e-paper
    display_plot_on_epaper(epd, plot_file)
    plot_active = True    # Mark plot as active
    first_plot = False    # Subsequent calls are not the first plot

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
        if first_plot:
            epd.init()  # Initialize the e-paper display
            epd.Clear()
            print("E-paper display initialized and cleared for the first plot.")
            first_plot = False
        else:
            print("Updating plot without reinitializing the display.")

        # Load and process the image
        image = Image.open(image_path)
        image = image.convert('1')
        image = image.resize((epd.width, epd.height), Image.ANTIALIAS)

        # Use partial update if available
        if hasattr(epd, 'displayPartial'):
            epd.displayPartial(epd.getbuffer(image))
            print("Plot updated using partial update.")
        else:
            epd.display(epd.getbuffer(image))
            print("Plot updated without reinitializing.")

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
