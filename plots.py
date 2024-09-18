import matplotlib.pyplot as plt
import os
import calendar
from PIL import Image

# Remove the epd initialization from plots.py
# epd = initialize_epaper()  # Remove this line
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
    
    shaded_days = {month: 0 for month in range(1, 13)}  # Initialize month counts to zero
    with open(file_path, 'r') as file:
        for line in file:
            values = line.strip().split(',')
            if len(values) >= 3:
                month, day, shape_type = map(int, values[:3])
                if shape_type == shape:
                    shaded_days[month] += 1  # Count the days shaded for the current shape
            else:
                continue  # Skip lines that don't have enough data
    return shaded_days

# Function to generate the plot as a PNG image and display it on the e-paper
def plot_year_data(epd, year, shape):
    global plot_active, shapes  # Ensure shapes is in scope

    shaded_days = read_shaded_days(year, shape)
    if not shaded_days:
        print("No shaded days found for the selected shape.")
        # Clear the e-paper display if there's no data
        epd.Clear()
        return

    # Plot the data
    months = [calendar.month_abbr[m] for m in shaded_days.keys()]
    days_count = list(shaded_days.values())

    # Adjust the figure size and DPI to match e-paper resolution (960x680)
    dpi = 100  # Adjust DPI if necessary
    fig_width = 960 / dpi  # 9.6 inches
    fig_height = 680 / dpi  # 6.8 inches

    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)
    fig.patch.set_facecolor('white')
    ax.bar(months, days_count, color='black')  # Use black color for e-paper
    ax.set_xlabel('Month')
    ax.set_ylabel('Number of Days Shaded')
    ax.set_title(f'{shapes[shape]} Shaded Days in {year}')
    ax.set_facecolor('white')  # Ensure background is white

    # Adjust font sizes for better readability on the e-paper display
    ax.title.set_fontsize(24)
    ax.xaxis.label.set_fontsize(20)
    ax.yaxis.label.set_fontsize(20)
    ax.tick_params(axis='both', which='major', labelsize=16)

    # Remove extra whitespace
    plt.tight_layout()

    # Save the plot as a .png image to display on the e-paper
    plot_file = '/tmp/plot.png'
    fig.savefig(plot_file, format='png', facecolor='white')
    plt.close(fig)  # Close the figure after saving

    # Load the image and display on the e-paper
    display_plot_on_epaper(epd, plot_file)
    plot_active = True  # Mark plot as active

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
        # Do not put the e-paper display to sleep here
        print("Plot displayed on the e-paper.")
    except Exception as e:
        print(f"Error displaying plot on e-paper: {e}")

# Function to close the plot and clear the e-paper display
def close_plot(epd):
    global plot_active
    try:
        epd.init()
        epd.Clear()  # Clear the e-paper screen to remove the plot
        # Do not put the e-paper display to sleep here
        plot_active = False
        print("Plot closed and e-paper display cleared.")
    except Exception as e:
        print(f"Error closing plot on e-paper: {e}")
        plot_active = False
