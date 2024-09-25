import time
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd13in3k  # Replace with your e-paper display module

def main():
    try:
        # Initialize the e-paper display
        epd = epd13in3k.EPD()
        epd.init()
        epd.Clear()
        print("E-paper display initialized and cleared.")

        # Create the first image
        image1 = Image.new('1', (epd.width, epd.height), 255)  # 255: white background
        draw = ImageDraw.Draw(image1)
        font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 48)
        draw.text((100, 100), 'First Image', font=font, fill=0)  # 0: black text

        # Display the first image
        epd.display(epd.getbuffer(image1))
        print("First image displayed.")
        time.sleep(5)  # Wait for 5 seconds

        # Create the second image
        image2 = Image.new('1', (epd.width, epd.height), 255)
        draw = ImageDraw.Draw(image2)
        draw.text((100, 200), 'Second Image', font=font, fill=0)

        # Update the display without reinitializing or clearing
        # Use partial update if available
        if hasattr(epd, 'displayPartial'):
            epd.displayPartial(epd.getbuffer(image2))
            print("Second image displayed using partial update.")
        else:
            epd.display(epd.getbuffer(image2))
            print("Second image displayed without reinitializing.")
        time.sleep(5)  # Wait for 5 seconds

        # Put the display to sleep
        epd.sleep()
        print("E-paper display put to sleep.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
#update