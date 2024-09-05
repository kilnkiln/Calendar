import calendar
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd13in3k   # Choose the right display model for your Waveshare display
import time

def generate_calendar_image(year, month):
    # Create a blank image with a white background
    img = Image.new('1', (250, 122), 255)  # 250x122 is a common size for Waveshare displays
    draw = ImageDraw.Draw(img)
    
    # Use a built-in font or load a TTF font
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)
    except IOError:
        font = ImageFont.load_default()

    # Generate the calendar text
    cal = calendar.TextCalendar(calendar.SUNDAY)
    cal_text = cal.formatmonth(year, month)

    # Draw the calendar text on the image
    draw.text((10, 10), cal_text, font=font, fill=0)

    # Return the image
    return img

def display_calendar(year, month):
    # Initialize the e-paper display
    epd = epd13in3k.EPD()
    epd.init()
    epd.Clear(0xFF)

    # Generate the calendar image
    img = generate_calendar_image(year, month)

    # Convert the image to the format required by the e-paper display
    epd.display(epd.getbuffer(img))

    # Put the display to sleep to save power
    epd.sleep()

if __name__ == '__main__':
    # Example: display the current month's calendar
    year = 2024
    month = 9
    display_calendar(year, month)

    # Wait for 10 seconds to view the display before clearing
    time.sleep(10)