import tkinter as tk
from waveshare_epd import epd13in3k
from PIL import Image, ImageDraw, ImageFont
import calendar
from datetime import datetime
import time

# Initialize the e-paper display with a full clear to avoid artifacts
def initialize_epaper():
    try:
        epd = epd13in3k.EPD()
        epd.init()  # Full initialization for the first display
        epd.Clear()  # Clear the display to ensure no residual images
        print("E-paper display initialized and cleared.")
        return epd
    except Exception as e:
        print(f"Error initializing e-paper display: {e}")
        return None

# Clear the full display before moving to partial refresh mode
def clear_display():
    if epd is not None:
        epd.init()  # Re-initialize the display (full mode)
        epd.Clear()  # Perform a full screen clear
        print("Full display cleared to remove any artifacts.")

# Initialize partial mode (called once after full refresh)
def init_partial_mode():
    try:
        epd.init()  # Ensure the display is initialized
        epd.Clear()  # Full refresh to clear artifacts
        epd.init_Part()  # Switch to partial mode after clearing
        print("Partial refresh mode initialized after clearing.")
    except Exception as e:
        print(f"Error initializing partial mode: {e}")

# Perform a full refresh whenever needed
def full_refresh():
    if epd is not None:
        epd.init()  # Initialize full mode
        epd.Clear()  # Clear the full screen
        print("Full refresh performed.")

# Function to render the full calendar and perform a full refresh
def render_calendar(year):
    global current_month_index, current_day_index, global_image

    if epd is None:
        print("E-paper display not initialized properly.")
        return

    try:
        # Create a blank image (1-bit, black-and-white)
        epd_width = epd.width
        epd_height = epd.height
        global_image = Image.new('1', (epd_width, epd_height), 255)  # 255 means white background

        # Create a drawing object to draw on the image
        draw = ImageDraw.Draw(global_image)

        # Define fonts (adjust paths if needed)
        font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
        font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)

        # Draw the year header at the top
        draw.text((epd_width // 2 - 50, 10), str(year), font=font_large, fill=0)

        # Get the starting weekday of January 1st (0 = Monday, 6 = Sunday)
        january_start_day, _ = calendar.monthrange(year, 1)

        # Define the starting X position for the weekday row and days
        start_x = 30  # Spacing between month label and day start
        weekday_y = 50  # Vertical position for the weekday header row

        # Draw a single continuous row for the weekdays at the top, starting at Jan 1st
        weekdays = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        for i in range(40):  # Loop to fill the width of the screen with repeating weekdays
            day_x = start_x + i * (20 + 5)
            weekday_index = (january_start_day + i) % 7
            draw.text((day_x, weekday_y), weekdays[weekday_index], font=font_small, fill=0)

        # Start drawing months and days staggered according to the start day of the month
        first_month_y = weekday_y + 30 + 15

        for month in range(1, 13):
            month_name = calendar.month_name[month][:3]
            month_y = first_month_y + (month - 1) * (30 + 15 + 5)
            start_day, num_days = calendar.monthrange(year, month)

            # Draw the shortened month name at the start of the row (left side)
            draw.text((5, month_y + (30 // 4)), month_name, font=font_small, fill=0)

            # Draw days of the month in a single row
            for day in range(1, num_days + 1):
                day_x = start_x + (start_day + day - 1) * (20 + 5)
                day_y = month_y

                text_x = day_x + (20 // 2) - 5
                text_y = day_y + (30 // 2) - 8

                # Draw the day number with a leading zero
                draw.text((text_x, text_y), str(day).zfill(2), font=font_small, fill=0)

        # Perform a full refresh for the initial calendar display
        epd.display(epd.getbuffer(global_image))  # Full refresh
    except Exception as e:
        print(f"Error displaying on e-paper: {e}")

# Initialize the e-paper display
epd = initialize_epaper()

# Initialize current selected day (for arrow key navigation)
current_date = datetime.now()
current_year = current_date.year
current_month_index = current_date.month - 1
current_day_index = current_date.day - 1  # Zero-based index for days

# Tkinter Setup for Key Bindings
root = tk.Tk()

# Make the window visible and larger so you can interact with it
root.geometry("400x200")  # Increase the window size for visibility
root.title("Calendar Controller")  # Set a title for the window
root.resizable(False, False)  # Disable resizing

# Clear display to avoid residual images
clear_display()

# Render the calendar and initialize partial mode
render_calendar(current_year)

# After full refresh, switch to partial refresh mode
init_partial_mode()  # Initialize partial mode once after clearing

# Example of moving the selection with right and left arrows
def move_selection(direction):
    global current_day_index, current_month_index

    old_day_index = current_day_index
    old_month_index = current_month_index

    if direction == "right":
        current_day_index += 1
        if current_day_index >= calendar.monthrange(current_year, current_month_index + 1)[1]:
            current_day_index = 0
            current_month_index = (current_month_index + 1) % 12
    elif direction == "left":
        current_day_index -= 1
        if current_day_index < 0:
            current_month_index = (current_month_index - 1) % 12
            current_day_index = calendar.monthrange(current_year, current_month_index + 1)[1] - 1

    # Here, you would call partial refresh and handle rendering

# Example of binding arrow keys for navigation
root.bind('<Right>', lambda event: move_selection("right"))
root.bind('<Left>', lambda event: move_selection("left"))

# Start the Tkinter event loop
root.mainloop()
