import tkinter as tk
from waveshare_epd import epd13in3k
from PIL import Image, ImageDraw, ImageFont
import calendar
from datetime import datetime

# Initialize the e-paper display
epd = epd13in3k.EPD()
epd.init()

# Define the weekdays row
weekdays = ['M', 'T', 'W', 'T', 'F', 'S', 'S']

# Create a set to store shaded days
shaded_days = set()

# Initialize the current selected day (for arrow key navigation)
current_date = datetime.now()
current_month_index = current_date.month - 1
current_day_index = current_date.day - 1  # Zero-based index for days

# Function to render the calendar and refresh the e-paper display
def render_calendar(year, selected_day=None):
    global current_month_index, current_day_index

    # Create a blank image (1-bit, black-and-white)
    epd_width = epd.width
    epd_height = epd.height
    image = Image.new('1', (epd_width, epd_height), 255)  # 255 means white background

    # Create a drawing object to draw on the image
    draw = ImageDraw.Draw(image)

    # Define fonts (adjust paths if needed)
    font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
    font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)

    # Draw the year header at the top
    draw.text((epd_width // 2 - 50, 10), str(year), font=font_large, fill=0)

    # Define dimensions for each day box
    day_width = 20
    day_height = 30
    padding = 5

    # Get the starting weekday of January 1st (0 = Monday, 6 = Sunday)
    january_start_day, _ = calendar.monthrange(year, 1)

    # Define the starting X position for the weekday row and days
    start_x = padding + 30  # Reduced spacing between month label and day start

    # Draw a single continuous row for the weekdays at the top, starting at Jan 1st
    weekday_y = 50  # Vertical position for the weekday header row
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

            # Draw the selection circle if the day is selected
            if month - 1 == current_month_index and day - 1 == current_day_index:
                draw.ellipse([day_x, day_y, day_x + day_width, day_y + day_height], outline=0, width=2)

            # Draw a shaded circle if the day is shaded
            if (month, day) in shaded_days:
                draw.ellipse([day_x + 3, day_y + 3, day_x + day_width - 3, day_y + day_height - 3], fill=0)

            # Draw the day number with a leading zero
            draw.text((text_x, text_y), str(day).zfill(2), font=font_small, fill=0)

    # Send the image to the e-paper display for a full refresh every time the calendar is updated
    epd.display(epd.getbuffer(image))
    epd.sleep()

# Function to move the selection circle with arrow keys
def move_selection(direction):
    global current_day_index, current_month_index

    if direction == "right":
        current_day_index += 1
        # Handle end of month and move to the next month
        if current_day_index >= calendar.monthrange(current_date.year, current_month_index + 1)[1]:
            current_day_index = 0
            current_month_index = (current_month_index + 1) % 12
    elif direction == "left":
        current_day_index -= 1
        # Handle start of month and move to the previous month
        if current_day_index < 0:
            current_month_index = (current_month_index - 1) % 12
            current_day_index = calendar.monthrange(current_date.year, current_month_index + 1)[1] - 1

    render_calendar(current_date.year)  # Refresh the display after movement

# Function to shade a day
def shade_day():
    global shaded_days
    current_day = (current_month_index + 1, current_day_index + 1)
    if current_day in shaded_days:
        shaded_days.remove(current_day)
    else:
        shaded_days.add(current_day)

    render_calendar(current_date.year)  # Refresh the display after shading

# Tkinter Setup for Key Bindings
root = tk.Tk()
root.withdraw()  # Hide the main window

# Bind keys to the movement and shading functions
root.bind('<Right>', lambda event: move_selection("right"))
root.bind('<Left>', lambda event: move_selection("left"))
root.bind('<space>', lambda event: shade_day())

# Start the Tkinter event loop to listen for key events
render_calendar(current_date.year)
root.mainloop()
