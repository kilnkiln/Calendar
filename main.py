import os
import tkinter as tk
from waveshare_epd import epd13in3k
from PIL import Image, ImageDraw, ImageFont
import calendar
from datetime import datetime
import plots  # Import the plots module

# Directory to store the calendar data
DATA_DIR = '/home/admin/CalendarDatabase'

# Initialize the e-paper display
def initialize_epaper():
    try:
        epd = epd13in3k.EPD()
        epd.init()  # Full initialization for the first display
        print("E-paper display initialized.")
        return epd
    except Exception as e:
        print(f"Error initializing e-paper display: {e}")
        return None

# Global variables to store the shaded days, selection ring, sleep timer, and sleep state
shaded_days = {}  # Store shaded days with their shape type
selection_ring_visible = False  # Start with the selection ring hidden
selection_ring_timer_id = None
refresh_timer_id = None
sleep_timer_id = None
display_asleep = False  # Track if the display is asleep
epd = initialize_epaper()  # Initialize the e-paper display

# Shape types: 1 = circle, 2 = square, 3 = triangle
current_shape = 1  # Default to circle
shapes = {1: "Circle", 2: "Square", 3: "Triangle"}

# View mode: 'calendar' or 'plot'
view_mode = 'calendar'

# Save shaded days with shape type to a file
def save_shaded_days(year):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    file_path = os.path.join(DATA_DIR, f'{year}.txt')

    with open(file_path, 'w') as file:
        for (month, day), shape in sorted(shaded_days.items()):
            file.write(f'{month},{day},{shape}\n')
    print(f"Shaded days saved to {file_path}")

# Updated function to load shaded days with shape type from a file
def load_shaded_days(year):
    global shaded_days  # Add this line to modify the global shaded_days
    file_path = os.path.join(DATA_DIR, f'{year}.txt')

    shaded_days.clear()  # Clear previous year's data

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                values = line.strip().split(',')
                if len(values) == 3:  # New format with month, day, and shape
                    month, day, shape = map(int, values)
                elif len(values) == 2:  # Old format with just month and day, default to circle (1)
                    month, day = map(int, values)
                    shape = 1  # Default to circle
                else:
                    continue  # Skip lines that don't match the expected format
                shaded_days[(month, day)] = shape
        print(f"Shaded days loaded from {file_path}")
    else:
        print(f"No file found for {year}. Creating new file...")
        save_shaded_days(year)

# Check if the e-paper display is asleep and wake it up
def check_and_wake_display():
    global display_asleep, epd
    if display_asleep:
        print("Waking up e-paper display...")
        try:
            epd = initialize_epaper()  # Reinitialize the display
            display_asleep = False
        except Exception as e:
            print(f"Error waking up e-paper display: {e}")

# Revert the selection ring to the current day after 30 seconds of inactivity
def revert_selection_to_current_day():
    global current_day_index, current_month_index, selection_ring_visible, current_date
    print("Reverting selection ring to current day.")

    # Set the selection ring back to the current date
    current_month_index = current_date.month - 1
    current_day_index = current_date.day - 1

    selection_ring_visible = True
    render_calendar(current_year)  # Redraw the calendar with the ring on the current day

# Put the e-paper display to sleep after 30 seconds of inactivity
def sleep_epaper():
    global display_asleep
    print("E-paper display going to sleep due to inactivity.")
    epd.sleep()
    display_asleep = True  # Mark the display as asleep

# Reset the timer to revert the selection ring and sleep the display
def reset_timers():
    global selection_ring_timer_id, sleep_timer_id

    # Reset the timer for reverting the selection ring
    if selection_ring_timer_id:
        root.after_cancel(selection_ring_timer_id)
    selection_ring_timer_id = root.after(500000, revert_selection_to_current_day)  # 30 seconds

    # Reset the timer for sleeping the e-paper display
    if sleep_timer_id:
        root.after_cancel(sleep_timer_id)
    sleep_timer_id = root.after(500000, sleep_epaper)  # 30 seconds for sleep

# Perform a quick refresh for the calendar display
def quick_refresh():
    try:
        check_and_wake_display()  # Ensure the e-paper is awake before refreshing
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

# Function to render the shapes in a row in the top right corner
def draw_shape_options(draw, shape_x, shape_y, font_small):
    # Adjusted for more spacing between the shapes and moved further to the right
    shape_spacing = 50  # Spacing between shapes

    # Display shapes in a single row with even spacing
    draw.ellipse([shape_x, shape_y, shape_x + 20, shape_y + 20], fill=0 if current_shape == 1 else None, outline=0)
    draw.rectangle([shape_x + shape_spacing, shape_y, shape_x + shape_spacing + 20, shape_y + 20], fill=0 if current_shape == 2 else None, outline=0)
    draw.polygon([shape_x + 2 * shape_spacing, shape_y + 20, shape_x + 2 * shape_spacing + 10, shape_y, shape_x + 2 * shape_spacing + 20, shape_y + 20], fill=0 if current_shape == 3 else None, outline=0)

# Main function to render the calendar
def render_calendar(year):
    global current_month_index, current_day_index, global_image, current_date

    if epd is None:
        print("E-paper display not initialized properly.")
        return

    try:
        check_and_wake_display()  # Ensure the display is awake before drawing

        # Create a new image with a white background
        image = Image.new('1', (epd.width, epd.height), 255)  # '1' for 1-bit color, 255 for white
        draw = ImageDraw.Draw(image)

        # Set fonts
        font_large = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSans.ttf', 36)
        font_small = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSans.ttf', 24)

        # Draw month and year at the top
        month_year_text = current_date.strftime("%B %Y")
        draw.text((epd.width // 2, 10), month_year_text, font=font_large, fill=0, anchor='ma')

        # Draw weekday labels at the top
        weekday_font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSans.ttf', 24)
        weekday_y = 60  # Y-coordinate for weekday labels
        dot_y = weekday_y + 25  # Y-coordinate for the dot under the weekday label
        weekday_x_positions = []  # To store x-positions of weekday labels

        cell_width = epd.width // 7  # Assuming 7 days in a week
        for i, weekday in enumerate(weekday_labels):
            x = i * cell_width + cell_width // 2
            weekday_x_positions.append(x)
            draw.text((x, weekday_y), weekday, font=weekday_font, fill=0, anchor='mm')

        # Calculate the weekday of the selected day
        selected_weekday = current_date.weekday()  # Monday is 0, Sunday is 6

        # Adjust if your weekday_labels start from Sunday
        # selected_weekday = (selected_weekday + 1) % 7  # If Sunday is 0

        # Draw the dot under the corresponding weekday label
        dot_radius = 5  # Adjust size as needed
        dot_x = weekday_x_positions[selected_weekday]
        draw.ellipse(
            (dot_x - dot_radius, dot_y - dot_radius, dot_x + dot_radius, dot_y + dot_radius),
            fill=0  # Black dot
        )

        # Draw the calendar grid
        calendar_y_start = dot_y + 20  # Starting Y-coordinate for the calendar grid
        cell_height = (epd.height - calendar_y_start) // 6  # Adjust rows as needed

        # Get the calendar for the current month
        cal = calendar.Calendar(firstweekday=0)  # 0 for Monday
        month_days = cal.monthdayscalendar(current_date.year, current_date.month)

        for week_index, week in enumerate(month_days):
            for day_index, day in enumerate(week):
                if day == 0:
                    continue  # Skip days outside the current month
                x = day_index * cell_width + cell_width // 2
                y = calendar_y_start + week_index * cell_height + cell_height // 2
                day_text = str(day)
                fill_color = 0  # Black text

                # Draw selection ring around the selected day
                if day == current_date.day:
                    ring_radius = min(cell_width, cell_height) // 2 - 5
                    draw.ellipse(
                        (x - ring_radius, y - ring_radius, x + ring_radius, y + ring_radius),
                        outline=0  # Black ring
                    )
                    # Optionally, you can fill the selected day with a different color

                draw.text((x, y), day_text, font=font_small, fill=fill_color, anchor='mm')

        # Send the image to the e-paper display
        epd.display(epd.getbuffer(image))
        epd.sleep()
    except Exception as e:
        print(f"Error displaying on e-paper: {e}")


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

    check_and_wake_display()  # Ensure display is awake before movement

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

# Function to change the calendar year
def change_year(delta):
    global current_year, current_date
    current_year += delta
    current_date = current_date.replace(year=current_year)
    load_shaded_days(current_year)
    if view_mode == 'calendar':
        render_calendar(current_year)
    else:
        plots.plot_year_data(epd,current_year, current_shape)  # Update the plot with the new year

# Example function to shade/unshade a day with the current shape and refresh the display
def shade_day():
    global shaded_days

    check_and_wake_display()  # Ensure display is awake before shading

    current_day = (current_month_index + 1, current_day_index + 1)

    # Toggle shading on the current day with the current shape
    if current_day in shaded_days and shaded_days[current_day] == current_shape:
        del shaded_days[current_day]
    else:
        shaded_days[current_day] = current_shape

    # Save the shaded days after any change
    save_shaded_days(current_year)

    # Reset the timer to hide the selection ring and sleep the display
    reset_timers()

    # Debounce the refresh (wait 1 second before refreshing)
    debounce_refresh()

# Function to change the current shape
def change_shape(shape):
    global current_shape
    current_shape = shape
    print(f"Shape changed to {shapes[shape]}")
    if view_mode == 'calendar':
        debounce_refresh()  # Refresh the display when the shape is changed
    else:
        # Update the plot with the new shape
        plots.plot_year_data(epd, current_year, current_shape)

# Function to handle the 'C' key press to toggle between calendar and plot
def toggle_plot():
    global view_mode
    if view_mode == 'calendar':
        plots.plot_year_data(epd, current_year, current_shape)  # Pass epd as an argument
        view_mode = 'plot'
    else:
        plots.close_plot(epd)  # Pass epd as an argument
        render_calendar(current_year)  # Return to calendar view
        view_mode = 'calendar'


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
root.bind('c', lambda event: toggle_plot())  # Toggle between calendar and plot

# Bind keys to shape selection (1 for Circle, 2 for Square, 3 for Triangle)
root.bind('1', lambda event: change_shape(1))
root.bind('2', lambda event: change_shape(2))
root.bind('3', lambda event: change_shape(3))

# Bind keys to change the year using 'a' and 'd'
root.bind('a', lambda event: change_year(-1))  # Press 'a' to go to the previous year
root.bind('d', lambda event: change_year(1))   # Press 'd' to go to the next year

# Start the Tkinter event loop
reset_timers()  # Start the selection ring and sleep timers
root.mainloop()
