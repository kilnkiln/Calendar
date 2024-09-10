import tkinter as tk
from waveshare_epd import epd13in3k
from PIL import Image, ImageDraw, ImageFont
import calendar
from datetime import datetime
import time

# Initialize the e-paper display
def initialize_epaper():
    try:
        epd = epd13in3k.EPD()
        epd.init()  # Full initialization for the first display
        return epd
    except Exception as e:
        print(f"Error initializing e-paper display: {e}")
        return None

# Initialize the display once
epd = initialize_epaper()

# Global image object to store the screen
global_image = None

# Calendar state
current_date = datetime.now()
current_year = current_date.year
current_month_index = current_date.month - 1
current_day_index = current_date.day - 1  # Zero-based index for days
shaded_days = set()  # Keep track of shaded days

# Circle settings
day_width = 20  # Width of a day block
circle_radius = 10
day_padding = 5  # Padding between days

# Font settings
font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)

# Define the weekdays row
weekdays = ['M', 'T', 'W', 'T', 'F', 'S', 'S']

# Render the calendar on the screen
def render_calendar():
    global global_image
    if epd is None:
        print("E-paper display not initialized properly.")
        return

    try:
        epd_width = epd.width
        epd_height = epd.height
        global_image = Image.new('1', (epd_width, epd_height), 255)  # 255 means white background

        # Create a drawing object to draw on the image
        draw = ImageDraw.Draw(global_image)

        # Starting position for the calendar layout
        start_x = 30
        start_y = 60

        # Draw the top row with weekdays
        for i in range(40):  # Repeating weekdays across the screen
            day_x = start_x + i * (day_width + day_padding)
            weekday_index = i % 7
            draw.text((day_x, start_y - 20), weekdays[weekday_index], font=font_small, fill=0)

        # Draw the months and the days
        for month in range(12):
            # Set the month name
            month_name = calendar.month_name[month + 1][:3]
            draw.text((start_x, start_y + month * (day_width + 15)), month_name, font=font_small, fill=0)

            # Draw days for the month
            start_day, num_days = calendar.monthrange(current_year, month + 1)
            for day in range(1, num_days + 1):
                day_x = start_x + (start_day + day - 1) * (day_width + day_padding)
                day_y = start_y + month * (day_width + 15)

                # Draw the selection circle if this is the current selected day
                if month == current_month_index and day - 1 == current_day_index:
                    draw.ellipse([day_x - circle_radius, day_y - circle_radius,
                                  day_x + circle_radius, day_y + circle_radius], outline=0, width=2)

                # Draw shaded circle if the day is shaded
                if (month, day) in shaded_days:
                    draw.ellipse([day_x - circle_radius, day_y - circle_radius,
                                  day_x + circle_radius, day_y + circle_radius], fill=0)

                # Draw the day number
                draw.text((day_x - 5, day_y - 8), str(day).zfill(2), font=font_small, fill=0)

        # Full refresh for the initial display
        epd.display(epd.getbuffer(global_image))
    except Exception as e:
        print(f"Error rendering calendar: {e}")

# Initialize partial refresh mode (called once)
def init_partial_mode():
    try:
        epd.init_Part()
        print("Partial refresh mode initialized")
    except Exception as e:
        print(f"Error initializing partial mode: {e}")

# Perform a partial refresh
def refresh_partial(x_start, y_start, x_end, y_end):
    global global_image
    try:
        # Perform a partial update
        epd.display_Partial(epd.getbuffer(global_image), x_start, y_start, x_end, y_end)
        print(f"Partial refresh: ({x_start}, {y_start}) to ({x_end}, {y_end})")
    except Exception as e:
        print(f"Error with partial refresh: {e}")

# Move the selection circle and perform a partial refresh
def move_selection(direction):
    global current_day_index, current_month_index

    if direction == "right":
        current_day_index += 1
        # Handle end of month and move to the next month
        if current_day_index >= calendar.monthrange(current_year, current_month_index + 1)[1]:
            current_day_index = 0
            current_month_index = (current_month_index + 1) % 12
    elif direction == "left":
        current_day_index -= 1
        # Handle start of month and move to the previous month
        if current_day_index < 0:
            current_month_index = (current_month_index - 1) % 12
            current_day_index = calendar.monthrange(current_year, current_month_index + 1)[1] - 1

    # Calculate the position of the day box for partial refresh
    start_day, _ = calendar.monthrange(current_year, current_month_index + 1)
    x_start = 30 + (start_day + current_day_index) * (day_width + day_padding) - circle_radius
    y_start = 60 + current_month_index * (day_width + 15) - circle_radius
    x_end = x_start + 2 * circle_radius
    y_end = y_start + 2 * circle_radius

    # Redraw the calendar
    render_calendar()

    # Perform partial refresh
    refresh_partial(x_start, y_start, x_end, y_end)

# Toggle shading of the selected day and perform a partial refresh
def toggle_shade():
    global shaded_days
    current_day = (current_month_index, current_day_index + 1)

    # Add or remove shading
    if current_day in shaded_days:
        shaded_days.remove(current_day)
    else:
        shaded_days.add(current_day)

    # Calculate the partial refresh area
    start_day, _ = calendar.monthrange(current_year, current_month_index + 1)
    x_start = 30 + (start_day + current_day_index) * (day_width + day_padding) - circle_radius
    y_start = 60 + current_month_index * (day_width + 15) - circle_radius
    x_end = x_start + 2 * circle_radius
    y_end = y_start + 2 * circle_radius

    # Redraw the calendar
    render_calendar()

    # Perform partial refresh
    refresh_partial(x_start, y_start, x_end, y_end)

# Tkinter Setup for Key Bindings
root = tk.Tk()

# Increase window size for visibility
root.geometry("400x200")
root.title("Partial Refresh Calendar")
root.resizable(False, False)

# Initialize partial mode
init_partial_mode()

# Initial render of the calendar
render_calendar()

# Bind keys for arrow navigation and shading
root.bind('<Right>', lambda event: move_selection("right"))
root.bind('<Left>', lambda event: move_selection("left"))
root.bind('<space>', lambda event: toggle_shade())

# Start Tkinter event loop
root.mainloop()
