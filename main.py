import os
import tkinter as tk
from waveshare_epd import epd13in3k
from PIL import Image, ImageDraw, ImageFont
import calendar
from datetime import datetime

# Directory to store the calendar data
DATA_DIR = '/home/admin/CalendarDatabase'

# Initialize the e-paper display with a quick refresh mode
def initialize_epaper():
    try:
        epd = epd13in3k.EPD()
        epd.init()  # Full initialization for the first display
        epd.Clear()  # Clear the display to ensure no residual images
        print("E-paper display initialized and cleared with full refresh.")
        return epd
    except Exception as e:
        print(f"Error initializing e-paper display: {e}")
        return None

# Global variables to store the shaded days, selection ring, sleep timer, and sleep state
shaded_days = set()
selection_ring_visible = False  # Start with the selection ring hidden
selection_ring_timer_id = None
refresh_timer_id = None
sleep_timer_id = None
display_asleep = False  # Track if the display is asleep

# Save shaded days to a file
def save_shaded_days(year):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    file_path = os.path.join(DATA_DIR, f'{year}.txt')

    with open(file_path, 'w') as file:
        for month, day in sorted(shaded_days):
            file.write(f'{month},{day}\n')
    print(f"Shaded days saved to {file_path}")

# Load shaded days from a file
def load_shaded_days(year):
    file_path = os.path.join(DATA_DIR, f'{year}.txt')

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                month, day = map(int, line.strip().split(','))
                shaded_days.add((month, day))
        print(f"Shaded days loaded from {file_path}")
    else:
        print(f"No file found for {year}. Creating new file...")
        save_shaded_days(year)

# Hide the selection ring after 30 seconds of inactivity
def hide_selection_ring():
    global selection_ring_visible
    selection_ring_visible = False
    render_calendar(current_year)  # Redraw the calendar without the ring

# Put the e-paper display to sleep after 30 seconds of inactivity
def sleep_epaper():
    global display_asleep
    print("E-paper display going to sleep due to inactivity.")
    epd.sleep()
    display_asleep = True  # Mark the display as asleep

# Wake up the e-paper display if it's asleep
def wake_up_epaper():
    global display_asleep
    if display_asleep:
        print("Waking up e-paper display...")
        try:
            epd.init()  # Full reinitialization
            epd.Clear()  # Clear the display to prevent artifacts
            display_asleep = False
        except Exception as e:
            print(f"Error waking up e-paper display: {e}")

# Reset the timer to hide the selection ring and sleep the display
def reset_timers():
    global selection_ring_timer_id, sleep_timer_id

    # Reset the timer for hiding the selection ring
    if selection_ring_timer_id:
        root.after_cancel(selection_ring_timer_id)
    selection_ring_timer_id = root.after(30000, hide_selection_ring)  # 30 seconds

    # Reset the timer for sleeping the e-paper display
    if sleep_timer_id:
        root.after_cancel(sleep_timer_id)
    sleep_timer_id = root.after(30000, sleep_epaper)  # 30 seconds

# Perform a quick refresh for the calendar display
def quick_refresh():
    try:
        wake_up_epaper()  # Ensure the e-paper is awake before refreshing
        epd.Clear(0xFF)  # Use a faster clear method (may not be available on all models)
        print("Quick refresh mode activated.")
    except Exception as e:
        print(f"Error during quick refresh: {e}")

# Debounce refresh logic
def debounce_refresh():
    global refresh_timer_id

    # If there's an existing timer, cancel it
    if refresh_timer_id:
        root.after_cancel(refresh_timer_id)

    # Set a new timer to refresh after 1 second
    refresh_timer_id = root.after(1000, lambda: render_calendar(current_year))

# Main function to render the calendar
def render_calendar(year):
    global current_month_index, current_day_index, global_image, current_date

    if epd is None:
        print("E-paper display not initialized properly.")
        return

    try:
        wake_up_epaper()  # Ensure the display is awake before drawing

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

                # Get the bounding box of the day number to center it
                bbox = draw.textbbox((0, 0), str(day).zfill(2), font=font_small)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                text_x = day_x + (20 - text_width) // 2  # Center horizontally
                text_y = day_y + (30 - text_height) // 2  # Center vertically

                # Center the circle around the day number
                circle_diameter = min(20, 30)  # Use the smaller of day_width and day_height
                circle_x = day_x + (20 - circle_diameter) // 2  # Center the circle horizontally
                circle_y = day_y + (30 - circle_diameter) // 2  # Center the circle vertically

                # Underline the current day (fixed underline)
                if month == current_date.month and day == current_date.day:
                    draw.line([day_x, day_y + 35, day_x + 20, day_y + 35], fill=0, width=2)

                # Draw the selection circle if the ring is visible and the day is selected
                if selection_ring_visible and month - 1 == current_month_index and day - 1 == current_day_index:
                    ring_padding = 3  # Add padding to make the ring larger than the shaded circle
                    draw.ellipse([circle_x - ring_padding, circle_y - ring_padding, 
                                  circle_x + circle_diameter + ring_padding, 
                                  circle_y + circle_diameter + ring_padding], 
                                  outline=0, width=2)

                # Draw a shaded circle if the day is shaded
                if (month, day) in shaded_days:
                    draw.ellipse([circle_x, circle_y, circle_x + circle_diameter, circle_y + circle_diameter], fill=0)

                # Draw the day number
                draw.text((text_x, text_y), str(day).zfill(2), font=font_small, fill=0)

        # Perform the quick refresh for the calendar display
        epd.display(epd.getbuffer(global_image))  # Quick refresh
        print("Quick refresh performed with updated calendar.")
    except Exception as e:
        print(f"Error displaying on e-paper: {e}")

# Initialize the e-paper display
epd = initialize_epaper()

# Initialize current selected day (for arrow key navigation)
current_date = datetime.now()
current_year = current_date.year
current_month_index = current_date.month - 1
current_day_index = current_date.day - 1  # Zero-based index for days

# Load the shaded days for the current year
load_shaded_days(current_year)

# Example function to update calendar on arrow key presses with debounce
def move_selection(direction):
    global current_day_index, current_month_index, selection_ring_visible

    if not selection_ring_visible:
        # Show the ring on the current day for the first key press
        selection_ring_visible = True
        debounce_refresh()
        return

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

    # Reset the timer to hide the selection ring and sleep the display
    reset_timers()

    # Debounce the refresh (wait 1 second before refreshing)
    debounce_refresh()

# Example function to shade/unshade a day and refresh the display
def shade_day():
    global shaded_days
    current_day = (current_month_index + 1, current_day_index + 1)

    # Toggle shading on the current day
    if current_day in shaded_days:
        shaded_days.remove(current_day)
    else:
        shaded_days.add(current_day)

    # Save the shaded days after any change
    save_shaded_days(current_year)

    # Reset the timer to hide the selection ring and sleep the display
    reset_timers()

    # Debounce the refresh (wait 1 second before refreshing)
    debounce_refresh()

# Tkinter Setup for Key Bindings
root = tk.Tk()

# Make the window visible and larger so you can interact with it
root.geometry("400x200")  # Increase the window size for visibility
root.title("Calendar Controller")  # Set a title for the window
root.resizable(False, False)  # Disable resizing

# Render the calendar on start
render_calendar(current_year)

# Bind keys to the movement and shading functions
root.bind('<Right>', lambda event: move_selection("right"))
root.bind('<Left>', lambda event: move_selection("left"))
root.bind('<space>', lambda event: shade_day())  # Spacebar to shade/unshade

# Start the Tkinter event loop
reset_timers()  # Start the selection ring and sleep timers
root.mainloop()
