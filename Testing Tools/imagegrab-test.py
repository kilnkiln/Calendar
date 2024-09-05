from PIL import ImageGrab
import os

def test_image_grab():
    try:
        # Capture a screenshot of the entire screen
        screenshot = ImageGrab.grab()
        # Save it to the CalendarDatabase directory
        directory = '/home/admin/CalendarDatabase'
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        image_path = os.path.join(directory, 'test_image.png')
        screenshot.save(image_path)
        print(f"Screenshot saved to {image_path}")
    except Exception as e:
        print(f"Error capturing screenshot: {e}")

test_image_grab()
