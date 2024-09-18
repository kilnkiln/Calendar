import matplotlib.pyplot as plt
import os
import calendar
from PIL import Image
from waveshare_epd import epd13in3k  # Import Waveshare e-paper library

# Initialize the e-paper display
def initialize_epaper():
    try:
        epd = epd13in3k.EPD()
        epd.init()  # Initialize the display
        print("E-paper display initialized for plotting.")
        return epd
    except Exception as e:
        print(f"Error initializing e-paper display for plotting: {e}")
        return None

epd = initialize_epaper()  # Initialize the e-paper display
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

# Function to generate the plot as a bitmap image and display it on the e-paper
def plot_year_data(year, shape):
    global plot_active, epd, shapes  # Ensure shapes is in scope

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
    # Figure size in inches = (width in pixels) / DPI
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
    ax.tick_params(axis='x', colors='black')
    ax.tick_params(axis='y', colors='black')
    ax.spines['bottom'].set_color('black')
    ax.spines['left'].set_color('black')
    ax.spines['top'].set_color('black')
    ax.spines['right'].set_color('black')
    ax.xaxis.label.set_color('black')
    ax.yaxis.label.set_color('black')
    ax.title.set_color('black')

    # Adjust font sizes for better readability on the e-paper display
    ax.title.set_fontsize(24)
    ax.xaxis.label.set_fontsize(20)
    ax.yaxis.label.set_fontsize(20)
    ax.tick_params(axis='both', which='major', labelsize=16)

    # Remove extra whitespace
    plt.tight_layout()

    # Save the plot as a .bmp image to display on the e-paper
    plot_file = '/tmp/plot.bmp'
    fig.savefig(plot_file, format='bmp', facecolor='white')
    plt.close(fig)  # Close the figure after saving to avoid display pop-up

    # Load the image and display on the e-paper
    display_plot_on_epaper(plot_file)
    plot_active = True  # Mark plot as active

# Function to display the plot on the e-paper display
def display_plot_on_epaper(image_path):
    global epd
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
        epd.sleep()  # Put the e-paper display to sleep to save power
        print("Plot displayed on the e-paper.")
    except Exception as e:
        print(f"Error displaying plot on e-paper: {e}")

# Function to close the e-paper display and return to calendar view
def close_plot():
    global plot_active, epd
    try:
        epd.init()
        epd.Clear()  # Clear the e-paper screen to remove the plot
        epd.sleep()
        plot_active = False
        print("Plot closed and e-paper display cleared.")
    except Exception as e:
        print(f"Error closing plot on e-paper: {e}")
        plot_active = False
