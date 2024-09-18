import matplotlib.pyplot as plt
import os
import calendar
from PIL import Image
from waveshare_epd import epd13in3k  # Import Waveshare e-paper library
from matplotlib.patches import Circle, Rectangle, Polygon
from matplotlib.ticker import MaxNLocator  # Import MaxNLocator if needed

# Remove the epd initialization from plots.py
# We'll pass the epd object from main.py
plot_active = False  # Track whether the plot is active

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
    global plot_active, shapes  # Ensure shapes is in scope

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

    # Plot the data as a line plot
    ax.plot(months, days_count, color='black', marker='o')

    # Set x-axis to months with abbreviations
    ax.set_xticks(months)
    ax.set_xticklabels([calendar.month_abbr[m] for m in months], fontsize=16)

    # Set y-axis from 1 to 31
    ax.set_ylim(1, 31)
    ax.set_yticks(range(1, 32))

    # Remove axis labels
    ax.set_xlabel('')
    ax.set_ylabel('')

    # Remove axis tick labels if desired (uncomment to remove)
    # ax.set_xticklabels([])
    # ax.set_yticklabels([])

    # Adjust y-axis to show integer ticks only (this line is optional since we set y-ticks explicitly)
    # ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    # Set title
    ax.set_title(f'{shapes[shape]} Shaded Days in {year}', fontsize=24, color='black')

    # Adjust font sizes for better readability
    ax.tick_params(axis='both', which='major', labelsize=16)

    # Remove extra whitespace
    plt.tight_layout()

    # Draw shapes in the top-right corner
    draw_shape_options(ax, shape)

    # Save the plot as a .png image to display on the e-paper
    plot_file = '/tmp/plot.png'
    fig.savefig(plot_file, format='png', facecolor='white')
    plt.close(fig)  # Close the figure after saving

    # Load the image and display on the e-paper
    display_plot_on_epaper(epd, plot_file)
    plot_active = True  # Mark plot as active

# Function to draw the shapes in the top-right corner and highlight the selected one
def draw_shape_options(ax, current_shape):
    # Define positions and sizes in axes coordinates
    shape_positions = [(0.85, 0.9), (0.90, 0.9), (0.95, 0.9)]  # Adjust positions as needed
    shape_size = 0.03  # Size in axes coordinates

    for i, (x, y) in enumerate(shape_positions):
        shape_type = i + 1  # Shape IDs start from 1
        if shape_type == 1:
            shape = Circle((x, y), shape_size / 2, transform=ax.transAxes,
                           fill=(current_shape == 1), edgecolor='black',
                           facecolor='black' if current_shape == 1 else 'white')
        elif shape_type == 2:
            shape = Rectangle((x - shape_size / 2, y - shape_size / 2),
                              shape_size, shape_size, transform=ax.transAxes,
                              fill=(current_shape == 2), edgecolor='black',
                              facecolor='black' if current_shape == 2 else 'white')
        elif shape_type == 3:
            triangle = [[x, y + shape_size / 2],
                        [x - shape_size / 2, y - shape_size / 2],
                        [x + shape_size / 2, y - shape_size / 2]]
            shape = Polygon(triangle, transform=ax.transAxes,
                            fill=(current_shape == 3), edgecolor='black',
                            facecolor='black' if current_shape == 3 else 'white')
        ax.add_patch(shape)

# Function to display the plot on the e-paper display
def display_plot_on_epaper(epd, image_path):
    try:
        epd.init()  # Initialize the e-paper
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

# Function to close the plot (no need to clear the e-paper display)
def close_plot(epd):
    global plot_active
    try:
        plot_active = False
        print("Plot closed.")
    except Exception as e:
        print(f"Error closing plot: {e}")
        plot_active = False
