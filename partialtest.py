import tkinter as tk
from waveshare_epd import epd13in3k
from PIL import Image, ImageDraw
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

# Global image object to store the screen
global_image = None

# Circle position and state
circle_x = 100  # Initial x position of the circle
circle_y = 100  # Fixed y position of the circle
circle_radius = 20
is_shaded = False  # Track if the circle is shaded

# Render the circle on the screen
def render_circle():
    global global_image
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

        # Draw the circle
        if is_shaded:
            draw.ellipse((circle_x - circle_radius, circle_y - circle_radius, 
                          circle_x + circle_radius, circle_y + circle_radius), fill=0)
        else:
            draw.ellipse((circle_x - circle_radius, circle_y - circle_radius, 
                          circle_x + circle_radius, circle_y + circle_radius), outline=0, width=2)

        # Display the full image initially
        epd.display(epd.getbuffer(global_image))
    except Exception as e:
        print(f"Error displaying circle on e-paper: {e}")

# Initialize partial mode
def init_partial_mode():
    try:
        epd.init_Part()
        print("Partial refresh mode initialized")
    except Exception as e:
        print(f"Error initializing partial mode: {e}")

# Perform partial refresh of the screen
def refresh_partial(x_start, y_start, x_end, y_end):
    global global_image
    try:
        # Perform a partial update
        epd.display_Partial(epd.getbuffer(global_image), x_start, y_start, x_end, y_end)
        print(f"Partial refresh: ({x_start}, {y_start}) to ({x_end}, {y_end})")
    except Exception as e:
        print(f"Error with partial refresh: {e}")

# Move the circle right/left and perform partial refresh
def move_circle(direction):
    global circle_x

    if direction == "right":
        circle_x += 20  # Move right
    elif direction == "left":
        circle_x -= 20  # Move left

    # Calculate the partial refresh area
    x_start = circle_x - circle_radius - 10
    y_start = circle_y - circle_radius - 10
    x_end = circle_x + circle_radius + 10
    y_end = circle_y + circle_radius + 10

    # Redraw the circle
    render_circle()

    # Perform partial refresh
    refresh_partial(x_start, y_start, x_end, y_end)

# Toggle shading of the circle with spacebar and perform partial refresh
def toggle_shade():
    global is_shaded
    is_shaded = not is_shaded

    # Calculate the partial refresh area
    x_start = circle_x - circle_radius - 10
    y_start = circle_y - circle_radius - 10
    x_end = circle_x + circle_radius + 10
    y_end = circle_y + circle_radius + 10

    # Redraw the circle
    render_circle()

    # Perform partial refresh
    refresh_partial(x_start, y_start, x_end, y_end)

# Tkinter Setup for Key Bindings
root = tk.Tk()

# Increase window size for visibility
root.geometry("400x200")
root.title("Partial Refresh Test")
root.resizable(False, False)

# Initialize partial mode
init_partial_mode()

# Initial render of the circle
render_circle()

# Bind arrow keys to move the circle
root.bind('<Right>', lambda event: move_circle("right"))
root.bind('<Left>', lambda event: move_circle("left"))
root.bind('<space>', lambda event: toggle_shade())  # Toggle shading with spacebar

# Start Tkinter event loop
root.mainloop()
