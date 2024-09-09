from waveshare_epd import epd13in3k
from PIL import Image, ImageDraw, ImageFont
import calendar
from datetime import datetime

# Initialize the e-paper display
epd = epd13in3k.EPD()
epd.init()

# Define the weekdays row
weekdays = ['M', 'T', 'W', 'T', 'F', 'S', 'S']

# Function to render the calendar
def render_calendar(year, highlighted_day=None):
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
    day_width = 20  # Adjust this value as needed to fit everything on screen
    day_height = 30
    padding = 5

    # Get the current date
    current_date = datetime.now()

    # Get the starting weekday of January 1st (0 = Monday, 6 = Sunday)
    january_start_day, _ = calendar.monthrange(year, 1)

    # Define the starting X position for the weekday row and days
    start_x = padding + 30  # Reduced spacing between month label and day start

    # Draw a single continuous row for the weekdays at the top, starting at Jan 1st
    weekday_y = 50  # Vertical position for the weekday header row
    for i in range(40):  # Loop to fill the width of the screen with repeating weekdays
        # Shift the weekday row to align with January 1st
        day_x = start_x + i * (day_width + padding)
        weekday_index = (january_start_day + i) % 7  # Shift starting point by January 1st's weekday
        draw.text((day_x, weekday_y), weekdays[weekday_index], font=font_small, fill=0)

    # Start drawing months and days staggered according to the start day of the month
    first_month_y = weekday_y + day_height + 15  # Adjusted spacing between weekday header and first month

    for month in range(1, 13):
        # Shorten the month name to the first three letters
        month_name = calendar.month_name[month][:3]

        # Set the y-position for each month's row, reducing vertical spacing
        month_y = first_month_y + (month - 1) * (day_height + padding + 15)  # Adjusted vertical spacing

        # Get month details: start day (0 = Monday, 6 = Sunday) and number of days
        start_day, num_days = calendar.monthrange(year, month)

        # Adjust the Y position of the month label to align it with the days
        month_label_y = month_y - (day_height // 2)  # Move the month label down slightly
        # Draw the shortened month name at the start of the row (left side)
        draw.text((padding, month_label_y), month_name, font=font_small, fill=0)

        # Draw days of the month in a single row, staggered based on the starting day of the week
        for day in range(1, num_days + 1):
            # Calculate the X position by offsetting the start day
            day_x = start_x + (start_day + day - 1) * (day_width + padding)
            day_y = month_y  # Keep the Y position in a single row per month

            # Center the day numbers under the weekday label by adjusting the X position
            text_x = day_x + (day_width // 2) - 5  # Center the day numbers
            text_y = day_y + (day_height // 2) - 8  # Adjust to vertically center the text

            # Highlight the current day with a rectangle if needed
            if month == current_date.month and day == current_date.day:
                draw.rectangle([day_x, day_y, day_x + day_width, day_y + day_height], outline=0, width=2)

            # Highlight the user-selected day if provided
            if highlighted_day and highlighted_day == (month, day):
                draw.rectangle([day_x, day_y, day_x + day_width, day_y + day_height], outline=0, width=2)
                # Display the day with a leading zero, centered
                draw.text((text_x, text_y), str(day).zfill(2), font=font_small, fill=0)
            else:
                draw.rectangle([day_x, day_y, day_x + day_width, day_y + day_height], outline=0)
                # Display the day with a leading zero, centered
                draw.text((text_x, text_y), str(day).zfill(2), font=font_small, fill=0)

    # Send the image to the e-paper display for a full refresh
    epd.display(epd.getbuffer(image))
    epd.sleep()

# Example usage:
current_year = datetime.now().year
render_calendar(current_year)
