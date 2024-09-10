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

# Global image object to store the entire calendar image
global_image = None

# Define the weekdays row
weekdays = ['M', 'T', 'W', 'T', 'F', 'S', 'S']

# Create a set to store shaded days
shaded_days = set()

# Initialize the current selected day (for arrow key navigation)
current_date = datetime.now()
current_year = current_date.year
current_month_index = current_date.month - 1
current_day_index = current_date.day - 1  # Zero-based index for days

# Dimensions for each day box
day_width = 20
day_height = 30
padding = 5

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
        start_x = padding + 30  # Spacing between month label and day start
        weekday_y = 50  # Vertical position for the weekday header row

        # Draw a single continuous row for the weekdays at the top, starting at Jan 1st
        for i in range(40):  # Loop to fill the width of the screen with repeating weekdays
            day_x = start_x + i * (day_width + padding)
            weekday_index = (january_start_day + i) % 7
            draw.text((day_x, weekday_y), weekdays[weekday_index], font=font_small, fill=0)

        # Start drawing months and days staggered according to the start day of the month
        first_month_y = weekday_y + day_height + 15

        for month in range(1, 13):
            month_name = calendar.month_name[month][:3]

            # Set the y-position for each month's row
            month_y = first_month_y + (month - 1) * (day_height + padding + 15)
            start_day, num_days = calendar.monthrange(year, month)

            # Draw the shortened month name at the start of the row (left side)
            draw.text((padding, month_y + (day_height // 4)), month_name, font=font_small, fill=0)

            # Draw days of the month in a single row
            for day in range(1, num_days + 1):
                day_x = start_x + (start_day + day - 1) * (day_width + padding)
                day_y = month_y

                text_x = day_x + (day_width // 2) - 5
                text_y = day_y + (day_height // 2) - 8

                # DEBUG: Log each day's position
                print(f"Month: {month}, Day: {day}, X: {day_x}, Y: {day_y}")

                # Draw the selection circle if the day is selected
                if month - 1 == current_month_index and day - 1 == current_day_index:
                    draw.ellipse([day_x, day_y, day_x + day_width, day_y + day_height], outline=0, width=2)

                # Draw a shaded circle if the day is shaded
                if (month, day) in shaded_days:
                    draw.ellipse([day_x + 3, day_y + 3, day_x + day_width - 3, day_y + day_height - 3], fill=0)

                # Draw the day number with a leading zero
                draw.text((text_x, text_y), str(day).zfill(2), font=font_small, fill=0)

        # Perform a full refresh for the initial calendar display
        epd.display(epd.getbuffer(global_image))  # Full refresh
    except Exception as e:
        print(f"Error displaying on e-paper: {e}")

# Function to render only the selected day for partial refresh
def render_partial_day(day_x, day_y, day_width, day_height, day, is_selected, is_shaded):
    global global_image
    draw = ImageDraw.Draw(global_image)

    # Clear the day area first (draw white rectangle) to avoid overlaps or artifacts
    draw.rectangle([day_x, day_y, day_x + day_width, day_y + day_height], fill=255)

    # Draw the selection circle if the day is selected
    if is_selected:
        draw.ellipse([day_x, day_y, day_x + day_width, day_y + day_height], outline=0, width=2)

    # Draw a shaded circle if the day is shaded
    if is_shaded:
        draw.ellipse([day_x + 3, day_y + 3, day_x + day_width - 3, day_y + day_height - 3], fill=0)

    # Draw the day number
    text_x = day_x + (day_width // 2) - 5
    text_y = day_y + (day_height // 2) - 8
    draw.text((text_x, text_y), str(day).zfill(2), font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14), fill=0)

# Initialize partial mode (called once after full refresh)
def init_partial_mode():
    try:
        epd.init_Part()  # Crucial: Initialize partial mode only once after full refresh
        print("Partial refresh mode initialized")
    except Exception as e:
        print(f"Error initializing partial mode: {e}")

# Function to perform a partial refresh
def refresh_partial(x_start, y_start, x_end, y_end):
    global global_image
    try:
        # Perform a partial update (refresh only the target area)
        print(f"Partial refresh at ({x_start}, {y_start}) to ({x_end}, {y_end})")  # DEBUG
        epd.display_Partial(epd.getbuffer(global_image), max(x_start - 2, 0), max(y_start - 2, 0), min(x_end + 2, epd.width), min(y_end + 2, epd.height))
    except Exception as e:
        print(f"Error with partial refresh: {e}")

# Function to calculate the bounding box for a day based on its position
def calculate_day_position(month_index, day_index):
    start_day, _ = calendar.monthrange(current_year, month_index + 1)
    
    # Fixing the X and Y position by adjusting the padding and day start calculations
    day_x = 30 + (start_day + day_index) * (day_width + padding)  # Adjusted X-coordinate
    day_y = 50 + month_index * (day_height + 15 + padding)  # Adjusted Y-coordinate to fix row alignment
    
    # DEBUG: Log the calculated coordinates
    print(f"Calculated position for Month: {month_index + 1}, Day: {day_index + 1} -> X: {day_x}, Y: {day_y}")
    
    return day_x, day_y

# Function to move the selection circle with arrow keys and perform a partial refresh
def move_selection(direction):
    global current_day_index, current_month_index

    old_day_index = current_day_index
    old_month_index = current_month_index

    # Move the selection based on the direction
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

    # Calculate the old and new positions
    old_day_x, old_day_y = calculate_day_position(old_month_index, old_day_index)
    new_day_x, new_day_y = calculate_day_position(current_month_index, current_day_index)

    # DEBUG: Log the coordinates for partial refresh
    print(f"Partial refresh (old): ({old_day_x}, {old_day_y}) to ({old_day_x + day_width}, {old_day_y + day_height})")
    print(f"Partial refresh (new): ({new_day_x}, {new_day_y}) to ({new_day_x + day_width}, {new_day_y + day_height})")

    # Redraw the old selection area (remove the circle)
    render_partial_day(old_day_x, old_day_y, day_width, day_height, old_day_index + 1, is_selected=False, is_shaded=(old_month_index + 1, old_day_index + 1) in shaded_days)

    # Redraw the new selection area (add the circle)
    render_partial_day(new_day_x, new_day_y, day_width, day_height, current_day_index + 1, is_selected=True, is_shaded=(current_month_index + 1, current_day_index + 1) in shaded_days)

    # Perform partial refresh **only once per area** to prevent multiple refreshes
    refresh_partial(old_day_x, old_day_y, old_day_x + day_width, old_day_y + day_height)  # Refresh old day area
    refresh_partial(new_day_x, new_day_y, new_day_x + day_width, new_day_y + day_height)  # Refresh new day area


# Function to shade/unshade a day (on spacebar press) and perform a partial refresh
def shade_day():
    global shaded_days
    current_day = (current_month_index + 1, current_day_index + 1)
    if current_day in shaded_days:
        shaded_days.remove(current_day)
    else:
        shaded_days.add(current_day)

    # Calculate the position of the day box for partial refresh
    day_x, day_y = calculate_day_position(current_month_index, current_day_index)

    # Redraw the day with shading/unshading
    render_partial_day(day_x, day_y, day_width, day_height, current_day_index + 1, is_selected=True, is_shaded=current_day in shaded_days)

    # Perform partial refresh for the shaded area
    refresh_partial(day_x, day_y, day_x + day_width, day_y + day_height)

# Tkinter Setup for Key Bindings
root = tk.Tk()

# Make the window visible and larger so you can interact with it
root.geometry("400x200")  # Increase the window size for visibility
root.title("Calendar Controller")  # Set a title for the window
root.resizable(False, False)  # Disable resizing

# First render of the calendar and full refresh
render_calendar(current_year)

# After full refresh, switch to partial refresh mode
init_partial_mode()  # Crucial: Initialize partial mode once, after full refresh

# Bind keys to the movement and shading functions
root.bind('<Right>', lambda event: move_selection("right"))  # Right arrow to move selection
root.bind('<Left>', lambda event: move_selection("left"))  # Left arrow to move selection
root.bind('<space>', lambda event: shade_day())  # Spacebar to shade/unshade

# Start the Tkinter event loop to listen for key events
root.mainloop()
