from solid import *
from solid.utils import *
import math
import os
from datetime import datetime

import pandas as pd
import numpy as np


def create_skyline_with_text(data, base_height=3.0, border_spacing=0.75,
                             label_text="Jacob Azoulay", label_text_right = "2024 NYC Marathon", filename="skyline_with_text.scad"):
    """
    Creates an OpenSCAD file with a skyline, flared base, and text.
    :param data: A 2D list (52x7) where each value represents progress (height of the block).
    :param base_height: Height of the base that will support the skyline.
    :param flare_angle: The angle in degrees to flare the base outward.
    :param border_spacing: Space between the grid and the base edge.
    :param label_text: Text to be embedded on the base.
    :param filename: Name of the output OpenSCAD file.
    """
    rows, cols = 52, 7  # 52 weeks and 7 days
    cube_size = 1.5  # Each cell's size in the grid (length/width)
    gap_between_cubes = -0.03
    total_width = rows * cube_size + (rows - 1) * gap_between_cubes
    total_depth = cols * cube_size + (cols - 1) * gap_between_cubes
    top_width = total_width + border_spacing * 2
    top_depth = total_depth + border_spacing * 2
    bottom_width = top_width + border_spacing * 2
    bottom_depth = top_depth + border_spacing * 2
    MAX_CUBE_HEIGHT = 20.0  # Maximum height of a cube
    max_height = max([max(row) for row in data])
    height_scale = MAX_CUBE_HEIGHT / max_height
    # logo_svg_path = "resources/logo.svg"
    scale_factor = 2

    # Create the flared base
    base_top = translate([border_spacing, border_spacing, -0.01])(
        cube([top_width, top_depth, 0.1])  # Flat top rectangle, level with the cubes
    )
    base_bottom = translate([0, 0, -base_height])(
        cube([bottom_width, bottom_depth, 0.1])  # Bottom larger base
    )
    flared_base = hull()(base_top + base_bottom)  # Connects top and bottom with flare

    # Create the skyline
    skyline = []
    for i in range(rows):
        for j in range(cols):
            height = data[i][j] * height_scale
            cube_pos = translate([2*border_spacing + i * (cube_size + gap_between_cubes), 2*border_spacing + j * (cube_size + gap_between_cubes), 0.2])(
                cube([cube_size, cube_size, height])
            )
            skyline.append(cube_pos)

    # Combine the base and the skyline
    skyline_model = flared_base + union()(skyline)
    # skyline_model = flared_base

    # Add text on top of the base
    # Define the angle of rotation
    flare_angle = math.degrees(math.atan(base_height / border_spacing))

    # Add text on top of the base and rotate it about the x-axis
    text_obj = translate([border_spacing * 2, border_spacing, -base_height * 0.75])(
        rotate([flare_angle, 0, 0])(  # Rotate about the x-axis
            linear_extrude(height=1)(
                text(label_text, size=1.5, halign="left")
            )
        )
    )

    # Add text on top of the base and rotate it about the x-axis
    text_obj_right = translate([bottom_width - border_spacing * 2, border_spacing, -base_height * 0.75])(
        rotate([flare_angle, 0, 0])(  # Rotate about the x-axis
            linear_extrude(height=1)(
                text(label_text_right, size=1.5, halign="right")
            )
        )
    )
    
    # Import the SVG file
    # svg_obj = import_(logo_svg_path)
    # # Scale down the SVG object
    # svg_obj = scale([0.01, 0.01, 0.01])(svg_obj)  # Adjust the scale factors as needed

    # # Apply the same transformations as text_obj
    # transformed_svg_obj = translate([bottom_width * 0.45, border_spacing, -base_height * 1])(
    #     rotate([flare_angle, 0, 0])(  # Rotate about the x-axis
    #         linear_extrude(height=1.25)(
    #             svg_obj
    #         )
    #     )
    # )

    # Final model with text and SVG object
    final_model = skyline_model + text_obj + text_obj_right #+ transformed_svg_obj
    final_model = scale([scale_factor, scale_factor, scale_factor])(final_model)

    # Save to OpenSCAD file
    save_path = os.path.join(filename)
    scad_render_to_file(final_model, save_path)
    print(f"OpenSCAD file with text saved as {save_path}")


def load_activity_data(csv_file, min_date="1/1/2024", max_date="12/31/2024"):
    # Make sure min and max dates are within same year
    min_date = datetime.strptime(min_date, "%m/%d/%Y")
    max_date = datetime.strptime(max_date, "%m/%d/%Y")
    assert min_date.year == max_date.year

    # Load CSV into a pandas DataFrame
    df = pd.read_csv(csv_file)

    df = df[df['Activity Type'] == 'Run']  # Filter for running activities only
    
    # Parse the 'Activity Date' column to datetime
    df['Activity Date'] = pd.to_datetime(df['Activity Date'], format='%b %d, %Y, %I:%M:%S %p')
    df = df[df['Activity Date'] >= min_date]  # Filter for min date
    df = df[df['Activity Date'] <= max_date]  # Filter for max date

    # Extract the year and week of year from the activity date
    df['Year'] = df['Activity Date'].dt.year
    df['Week'] = df['Activity Date'].dt.isocalendar().week
    df['DayOfWeek'] = df['Activity Date'].dt.weekday  # Monday = 0, Sunday = 6

    # Create a 7x52 grid initialized with zeros (7 days x 52 weeks)
    progress_data = np.zeros((52, 7))

    # Iterate over the DataFrame to fill the grid
    for index, row in df.iterrows():
        week = row['Week'] - 1  # Week is 1-indexed, so subtract 1
        day = row['DayOfWeek']  # DayOfWeek is already 0-indexed (Monday = 0)
        distance = row['Distance'] * 0.621371  # Convert km to miles
        
        # Add the distance to the corresponding day in the 7x52 grid
        progress_data[week][day] += distance

    # Convert the NumPy array to a list of lists
    progress_data = progress_data.tolist()

    print("\n\nProgress Data for skyline:")
    for row in progress_data:
        print([round(val, 2) for val in row])
    
    return progress_data


if __name__ == "__main__":
    # Use the function
    csv_file = os.path.join("raw_strava_data", "export_5", "activities.csv")
    skyline_progress_data = load_activity_data(csv_file)

    # # Create the OpenSCAD file with the flared base and text
    create_skyline_with_text(skyline_progress_data, filename="skyline_5.scad")
