import matplotlib.pyplot as plt
import os
import calendar
from PIL import Image
from waveshare_epd import epd13in3k  # Import Waveshare e-paper library

epd = epd13in3k.EPD()  # Initialize the e-paper display
plot_active = False  # Track whether the plot is active

# Function to read the shaded days from the txt file for the selected year and shape
def read_shaded_days(year, shape):
    data_dir = '/home/admin/CalendarDatabase'
    file_path = os.path.join(data_dir, f'{year}.txt')
    if not os.path.exists(file_path):
        print(f"No data for {year}.")
        return []

    shaded_days = {month: 0 for month in range(1, 13)}  # Initialize month counts to zero
    with open(file_path, 'r') as file:
        for line in file:
            month, day, shape_type = map(int, line.strip().split(','))
            if shape_type == shape:
                shaded_days[month] += 1  # Count the days shaded for the current shape

    return shaded_days

# Function to generate the plot as a bitmap image
def plot_year_data(year, shape):
    global plot_active

    shaded_days = read_shaded_days(year, shape)
    if not shaded_days:
        print("No shaded days found for the selected shape.")
        return

    # Plot the data
    months = [calendar.month_abbr[m] for m in shaded_days.keys()]
    days_count = list(shaded_days.values())

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(months, days_count, color='blue')
    ax.set_xlabel('Month')
    ax.set_ylabel('Number of Days Shaded')
    ax.set_title(f'{shapes[shape]} Shaded Days in {year}')

    # Save the plot as a .bmp image to display on the e-paper
    plot_file = '/tmp/plot.bmp'
    fig.savefig(plot_file, format='bmp')
    plt.close(fig)  # Close the figure after saving to avoid display pop-up

    # Load the image and display on the e-paper
    display_plot_on_epaper(plot_file)

# Function to display the plot on the e-paper display
def display_plot_on_epaper(image_path):
    try:
        epd.init()  # Initialize the e-paper
        epd.Clear()  # Clear the display
        image = Image.open(image_path)
        epd.display(epd.getbuffer(image))  # Send the image buffer to the display
        epd.sleep()  # Put the e-paper display to sleep to save power
        print("Plot displayed on the e-paper.")
    except Exception as e:
        print(f"Error displaying plot on e-paper: {e}")

# Function to close the e-paper display and return to calendar view
def close_plot():
    global plot_active
    epd.Clear()  # Clear the e-paper screen to remove the plot
    plot_active = False
