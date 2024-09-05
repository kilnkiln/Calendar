import tkinter as tk
import calendar
from datetime import datetime
import os
from PIL import ImageGrab  # To capture the screen as an image
from PIL import Image
import plots  # Import the plots module
from waveshare_epd import epd13in3k  # Import the Waveshare e-Paper library for display

def generate_calendar_matrix(year):
    # List to hold the calendar rowsepaper
    calendar_matrix = []
    
    # Iterate through each month of the year
    for month in range(1, 13):
        # Get the starting day of the month (0=Monday, ..., 6=Sunday)
        start_day = calendar.monthrange(year, month)[0]
        # Get the number of days in the month
        num_days = calendar.monthrange(year, month)[1]
        # Get the month name
        month_name = calendar.month_name[month]

        # Create the row for the current month with month name at the start
        # The row should have 7 slots (1 for each weekday) + max 31 days + 1 for month name
        month_row = [month_name] + [''] * (7 + num_days)
        
        # Place the days of the month in the correct positions
        for day in range(1, num_days + 1):
            position = start_day + day - 1  # adjust position for zero-based index
            month_row[position + 1] = day  # +1 to account for month name in position 0
        
        # Append the row to the matrix
        calendar_matrix.append(month_row)

    return calendar_matrix

# Function to update the e-ink display with the current calendar view
def update_eink_display():
    epd = epd13in3k.EPD()
    epd.init()
    epd.Clear()

    # Capture the current calendar window as an image
    x0 = root.winfo_rootx()
    y0 = root.winfo_rooty()
    x1 = x0 + root.winfo_width()
    y1 = y0 + root.winfo_height()

    # Save the screenshot of the window
    screenshot = ImageGrab.grab(bbox=(x0, y0, x1, y1))
    image_directory = '/home/admin/CalendarDatabase'
    image_path = os.path.join(image_directory, 'calendar_view.png')
    try:
        screenshot.save(image_path)
    except Exception as e:
        print(f"Error saving image: {e}")

    screenshot.save("calendar_view.png")

    # Display the screenshot on the e-ink screen
    try:
        image = Image.open(image_path)
        epd.display(epd.getbuffer(image))
        epd.sleep()
    except Exception as e:
        print(f"Error displaying image on e-paper: {e}")
    
def display_calendar(year):
    # Directory for saving calendar data
    directory = '/home/admin/CalendarDatabase'
    if not os.path.exists(directory):
        os.makedirs(directory)

    # File path for the current year's data
    file_path = os.path.join(directory, f'{year}.txt')

    # Create the main window
    root = tk.Tk()
    root.title(f"Calendar for {year}")

    # Set the window to full screen
    root.attributes('-fullscreen', True)

    # Function to toggle full-screen mode
    def toggle_fullscreen(event=None):
        is_fullscreen = root.attributes('-fullscreen')
        root.attributes('-fullscreen', not is_fullscreen)

    # Bind the Escape key to exit full-screen mode
    root.bind('<Escape>', toggle_fullscreen)

    # Set the background color of the main window to white
    root.configure(bg='white')

    # Create a frame to center the calendar content
    frame = tk.Frame(root, bg='white')
    frame.place(relx=0.5, rely=0.5, anchor='center')

    # Generate the calendar matrix
    calendar_matrix = generate_calendar_matrix(year)
    
    # Define column width
    day_width = 30

    # Define the labels for the days of the week
    weekday_abbr = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
    
    # Calculate the number of columns needed to center the year
    num_columns = len(weekday_abbr) + 31  # 7 for weekdays, 31 for max days in a month

    # Display the year as a centered header
    header = tk.Label(frame, text=str(year), font=('Arial', 16), anchor='center', bg='white')
    header.grid(row=0, column=0, columnspan=num_columns, pady=10)

    # Display the weekdays as the top row, repeating them for a full width
    for i in range(1, 37):  # Columns 1 to 31 for days of the month
        day_label = tk.Label(frame, text=weekday_abbr[(i - 1) % 7], font=('Arial', 10, 'bold'), bg='white')
        day_label.grid(row=1, column=i, padx=2, pady=2, sticky='nsew')

    # Get the current date
    current_date = datetime.now()
    current_month = current_date.month
    current_day = current_date.day

    # Store references to day canvases for toggling circles and navigation
    day_canvases = {}
    month_days = [calendar.monthrange(year, month)[1] for month in range(1, 13)]

    # Initialize current position to today's date
    current_month_index = current_month - 1
    current_day_index = current_date.day

    # Timer ID for ring disappearance
    ring_timer_id = None

    # Set to keep track of shaded days
    shaded_days = set()

    # Flag to check if selection has started
    selection_started = False

    # Function to draw the selection ring around the current day
    def draw_selection_ring():
        for (month_idx, day_idx), canvas in day_canvases.items():
            canvas.delete('ring')
            if month_idx == current_month_index and day_idx == current_day_index:
                canvas.create_oval(2, 2, day_width - 2, day_width - 2, outline='gray', width=2, tags='ring')

    # Function to toggle the circle on a day
    def toggle_circle(month_idx, day_idx):
        canvas = day_canvases.get((month_idx, day_idx))
        if canvas:
            if 'circle' in canvas.gettags('circle'):
                canvas.delete('circle')
                shaded_days.discard((month_idx, day_idx))
            else:
                canvas.create_oval(5, 5, day_width - 5, day_width - 5, fill='black', tags='circle')
                shaded_days.add((month_idx, day_idx))
            save_shaded_days()

    # Function to move selection with arrow keys
    def move_selection(event):
        nonlocal current_month_index, current_day_index, ring_timer_id, selection_started

        # Check if selection has started
        if not selection_started:
            # Move the ring to the current day
            current_month_index = current_month - 1
            current_day_index = current_date.day
            selection_started = True
            draw_selection_ring()
            return

        if event.keysym == 'Right':
            next_day_index = current_day_index + 1
            if next_day_index <= month_days[current_month_index]:
                current_day_index = next_day_index
            elif current_month_index < 11:
                current_month_index += 1
                current_day_index = 1
                while current_day_index > month_days[current_month_index] or (current_month_index, current_day_index) not in day_canvases:
                    current_day_index += 1

        elif event.keysym == 'Left':
            prev_day_index = current_day_index - 1
            if prev_day_index > 0:
                current_day_index = prev_day_index
            elif current_month_index > 0:
                current_month_index -= 1
                current_day_index = month_days[current_month_index]
                while current_day_index > month_days[current_month_index] or (current_month_index, current_day_index) not in day_canvases:
                    current_day_index -= 1

        elif event.keysym == 'Down':
            next_month_index = current_month_index + 1
            if next_month_index <= 11:
                current_month_index = next_month_index
                if current_day_index > month_days[current_month_index]:
                    current_day_index = month_days[current_month_index]
                while current_day_index > month_days[current_month_index] or (current_month_index, current_day_index) not in day_canvases:
                    current_day_index -= 1

        elif event.keysym == 'Up':
            prev_month_index = current_month_index - 1
            if prev_month_index >= 0:
                current_month_index = prev_month_index
                if current_day_index > month_days[current_month_index]:
                    current_day_index = month_days[current_month_index]
                while current_day_index > month_days[current_month_index] or (current_month_index, current_day_index) not in day_canvases:
                    current_day_index -= 1

        # Draw the ring after moving
        draw_selection_ring()

        # Reset the timer
        if ring_timer_id is not None:
            root.after_cancel(ring_timer_id)
        ring_timer_id = root.after(60000, clear_selection_ring)  # 60 seconds

    # Function to toggle shading with the space bar
    def toggle_shading(event):
        toggle_circle(current_month_index, current_day_index)

    # Function to clear the selection ring after a timeout
    def clear_selection_ring():
        nonlocal selection_started
        for canvas in day_canvases.values():
            canvas.delete('ring')
        selection_started = False

    # Function to save shaded days to a file
    def save_shaded_days():
        with open(file_path, 'w') as file:
            for month_idx, day_idx in sorted(shaded_days):
                file.write(f"{month_idx + 1},{day_idx}\n")

    # Function to load shaded days from a file
    def load_shaded_days():
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                for line in file:
                    month_idx, day_idx = map(int, line.strip().split(','))
                    shaded_days.add((month_idx - 1, day_idx))
                    canvas = day_canvases.get((month_idx - 1, day_idx))
                    if canvas:
                        canvas.create_oval(5, 5, day_width - 5, day_width - 5, fill='black', tags='circle')

    # Function to open the plots window
    def open_plots(event=None):
        plots.display_plots()

    # Add a button to open the plots window
    plots_button = tk.Button(frame, text="Show Plots", command=open_plots)
    plots_button.grid(row=0, column=num_columns, padx=10, pady=10, sticky='e')
    
    # Bind key events
    root.bind('<Right>', move_selection)
    root.bind('<Left>', move_selection)
    root.bind('<Down>', move_selection)
    root.bind('<Up>', move_selection)
    root.bind('<space>', toggle_shading)
    root.bind('<c>', open_plots)  # Bind 'C' key to open the plots window

    # Display the month rows
    for month_index, row in enumerate(calendar_matrix):
        # Display the month name
        month_label = tk.Label(frame, text=row[0], font=('Arial', 10, 'bold'), bg='white')
        month_label.grid(row=month_index + 2, column=0, padx=5, pady=5, sticky="W")

        # Display the days of the month
        for day_index in range(1, len(row)):
            day = row[day_index]
            if day != '':
                # Create a canvas for each day to allow for drawing
                canvas = tk.Canvas(frame, width=day_width, height=day_width, bg='white', highlightthickness=0)
                canvas.create_text(day_width / 2, day_width / 2, text=str(day).zfill(2), font=('Arial', 10), tags='day')
                canvas.grid(row=month_index + 2, column=day_index, padx=2, pady=2, sticky='nsew')
                
                # Store the canvas reference for toggling and navigation
                day_canvases[(month_index, day)] = canvas

                # Highlight the current day with a line
                if month_index + 1 == current_month and day == current_day:
                    canvas.create_line(0, day_width - 2, day_width, day_width - 2, fill='red', width=2, tags='current')

    # Load previously shaded days from the file
    load_shaded_days()

    # Run the application
    root.mainloop()

# Load the current year
current_year = datetime.now().year
display_calendar(current_year)
update_eink_display()  # Call the e-ink update after displaying the calendar