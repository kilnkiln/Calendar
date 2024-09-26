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

        # Draw shape options in a row at the top right
        shape_x = epd_width - 180  # Moved further right
        shape_y = 20
        draw_shape_options(draw, shape_x, shape_y, font_small)

        # Adjust these parameters to control spacing
        weekday_y = 80  # Move the weekdays lower by increasing this value
        first_month_y = weekday_y + 40  # Adjust this to maintain the spacing between weekdays and month rows

        # Get the starting weekday of January 1st (0 = Monday, 6 = Sunday)
        january_start_day, _ = calendar.monthrange(year, 1)

        # Define the starting X position for the weekday row and days
        start_x = 30  # Spacing between month label and day start
        day_width = 25  # Width of each day cell (including spacing)

        # Initialize selected_day_x to store the x-coordinate of the selected day
        selected_day_x = None

        # Center the weekday labels above the corresponding days
        weekdays = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        for i in range(40):  # Loop to fill the width of the screen with repeating weekdays
            day_x = start_x + i * day_width
            weekday_index = (january_start_day + i) % 7

            # Calculate the center position of the weekday label
            bbox = draw.textbbox((0, 0), weekdays[weekday_index], font=font_small)
            text_width = bbox[2] - bbox[0]
            text_x = day_x + (day_width - text_width) // 2

            draw.text((text_x, weekday_y), weekdays[weekday_index], font=font_small, fill=0)

        # Start drawing months and days staggered according to the start day of the month
        for month in range(1, 13):
            month_name = calendar.month_name[month][:3]

            # Adjust spacing between month rows
            month_y = first_month_y + (month - 1) * (30 + 10 + 5)  # Adjust '10' to control spacing between month rows

            # Adjust the position of the month label to align with day numbers
            draw.text((5, month_y + (30 // 2)), month_name, font=font_small, fill=0)  # Adjust this value to align the month name with the days

            start_day, num_days = calendar.monthrange(year, month)

            # Draw days of the month in a single row
            for day in range(1, num_days + 1):
                day_x = start_x + (start_day + day - 1) * day_width
                day_y = month_y

                # Get the bounding box of the day number to center it
                bbox = draw.textbbox((0, 0), str(day).zfill(2), font=font_small)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                text_x = day_x + (day_width - text_width) // 2  # Center horizontally
                text_y = day_y + (30 - text_height) // 2  # Center vertically

                # Center the shape (circle, square, triangle) around the day number
                shape_diameter = min(20, 30)  # Use the smaller of day_width and day_height
                shape_x = day_x + (day_width - shape_diameter) // 2  # Center the shape horizontally
                shape_y = day_y + (30 - shape_diameter) // 2  # Center the shape vertically

                # Underline the current day (fixed underline)
                if month == current_date.month and day == current_date.day:
                    draw.line([day_x, day_y + 35, day_x + day_width, day_y + 35], fill=0, width=2)
                    # Record the x-coordinate of the selected day
                    selected_day_x = day_x

                # Draw the selection shape if the ring is visible and the day is selected
                if selection_ring_visible and month - 1 == current_month_index and day - 1 == current_day_index:
                    if current_shape == 1:  # Circle
                        draw.ellipse([shape_x - 3, shape_y - 3, shape_x + shape_diameter + 3, shape_y + shape_diameter + 3], outline=0, width=2)
                    elif current_shape == 2:  # Square
                        draw.rectangle([shape_x - 3, shape_y - 3, shape_x + shape_diameter + 3, shape_y + shape_diameter + 3], outline=0, width=2)
                    elif current_shape == 3:  # Triangle
                        draw.polygon([shape_x, shape_y + shape_diameter, shape_x + shape_diameter / 2, shape_y,
                                      shape_x + shape_diameter, shape_y + shape_diameter], outline=0, width=2)

                # Draw a shaded shape if the day is shaded and the current shape matches
                if (month, day) in shaded_days and shaded_days[(month, day)] == current_shape:
                    if current_shape == 1:  # Circle
                        draw.ellipse([shape_x, shape_y, shape_x + shape_diameter, shape_y + shape_diameter], fill=0)
                    elif current_shape == 2:  # Square
                        draw.rectangle([shape_x, shape_y, shape_x + shape_diameter, shape_y + shape_diameter], fill=0)
                    elif current_shape == 3:  # Triangle
                        draw.polygon([shape_x, shape_y + shape_diameter, shape_x + shape_diameter / 2, shape_y,
                                      shape_x + shape_diameter, shape_y + shape_diameter], fill=0)

                # Draw the day number
                draw.text((text_x, text_y), str(day).zfill(2), font=font_small, fill=0)

        # Draw the dot under the weekday label corresponding to the selected day
        if selected_day_x is not None:
            dot_radius = 3  # Adjust size as needed
            dot_y = weekday_y + font_small.getsize('M')[1] + 5  # Position below the weekday label
            dot_x = selected_day_x + day_width // 2  # Center of the day cell

            draw.ellipse(
                (dot_x - dot_radius, dot_y - dot_radius, dot_x + dot_radius, dot_y + dot_radius),
                fill=0  # Black dot
            )

        # Perform the quick refresh for the calendar display
        epd.display(epd.getbuffer(global_image))  # Quick refresh
        print("Quick refresh performed with updated calendar.")
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
