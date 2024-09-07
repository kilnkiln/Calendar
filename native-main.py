from waveshare_epd import epd13in3k
from PIL import Image, ImageDraw, ImageFont
import calendar
from datetime import datetime

# Initialize the e-paper display
epd = epd13in3k.EPD()
epd.init()

# Function to render the entire calendar
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

    # Draw the year header
    draw.text((epd_width // 2 - 50, 10), str(year), font=font_large, fill=0)

    # Define dimensions for each day box
    day_width = 30
    day_height = 30
    padding = 5

    # Get the current date
    current_date = datetime.now()

    # Start drawing months and days
    for month in range(1, 13):
        month_name = calendar.month_name[month]
        month_x = padding
        month_y = 50 + (month - 1) * (day_height + padding)  # Adjust Y position for each month

        # Draw the month name
        draw.text((month_x, month_y), month_name, font=font_small, fill=0)

        # Get month details
        start_day, num_days = calendar.monthrange(year, month)

        # Draw days for the month
        for day in range(1, num_days + 1):
            day_x = month_x + (day - 1 + start_day) % 7 * (day_width + padding)
            day_y = month_y + (day - 1 + start_day) // 7 * (day_height + padding) + 20

            # Highlight the current day with a rectangle if needed
            if month == current_date.month and day == current_date.day:
                draw.rectangle([day_x, day_y, day_x + day_width, day_y + day_height], outline=0, width=2)

            # Highlight the user-selected day if provided
            if highlighted_day and highlighted_day == (month, day):
                draw.rectangle([day_x, day_y, day_x + day_width, day_y + day_height], outline=0, width=2)
                draw.text((day_x + 10, day_y + 5), str(day), font=font_small, fill=0)
            else:
                draw.rectangle([day_x, day_y, day_x + day_width, day_y + day_height], outline=0)
                draw.text((day_x + 10, day_y + 5), str(day), font=font_small, fill=0)

    # Send the image to the e-paper display for a full refresh
    epd.display(epd.getbuffer(image))
    epd.sleep()

# Example usage:
current_year = datetime.now().year
render_calendar(current_year)