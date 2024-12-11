import stravavis
import stravavis.process_data
import stravavis.process_activities
import stravavis.plot_facets
import stravavis.plot_elevations
import stravavis.plot_landscape
import stravavis.plot_map
import stravavis.plot_calendar
import stravavis.plot_dumbbell
import skyline
import os
import gzip
import shutil
import datetime


def unzip_files_in_directory(directory):

    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.gz'):
            gz_file_path = os.path.join(directory, filename)
            unzipped_file_path = os.path.join(directory, filename[:-3])  # Remove '.gz' extension

            # Unzip the file
            with gzip.open(gz_file_path, 'rb') as f_in:
                with open(unzipped_file_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(gz_file_path)
            print(f'Unzipped: {filename} -> {unzipped_file_path}')


def main():
    # Define paths
    path = R"C:\Users\Jacazo\OneDrive - ASSA ABLOY Group\Repos\Misc\Stava\raw_strava_data\export_post_marathon"
    activities_data_path = os.path.join(path, "activities")
    activities_csv_path = os.path.join(path, "activities.csv")

    min_date = "1/1/2024"
    max_date = "11/4/2024"

    # Get the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create a subdirectory with the timestamp
    output_dir = os.path.join("output", timestamp)
    os.makedirs(output_dir, exist_ok=True)

    # Process the data and activities
    unzip_files_in_directory(activities_data_path)
    filenames = [os.path.join(activities_data_path, filename) for filename in os.listdir(activities_data_path)]
    processed_data = stravavis.process_data.process_data(filenames, min_date=min_date, max_date=max_date)
    activities = stravavis.process_activities.process_activities(activities_csv_path, min_date=min_date, max_date=max_date)

    # Generate and save various plots with timestamp
    stravavis.plot_facets.plot_facets(processed_data, output_file=os.path.join(output_dir, f"facets_plot.png"), ncol=8)
    stravavis.plot_facets.plot_facets(processed_data, output_file=os.path.join(output_dir, f"facets_plot_square.png"), ncol=None)
    stravavis.plot_elevations.plot_elevations(processed_data, output_file=os.path.join(output_dir, f"elevations_plot.png"))
    stravavis.plot_landscape.plot_landscape(processed_data, output_file=os.path.join(output_dir, f"landscape_plot.png"))
    stravavis.plot_map.plot_map(processed_data, output_file=os.path.join(output_dir, f"map_plot_NH.png"),    
                                lat_min=41.259572,
                                lat_max=41.436194,
                                lon_min=-73.017393,
                                lon_max=-72.721782)
    stravavis.plot_map.plot_map(processed_data, output_file=os.path.join(output_dir, f"map_plot_Bx.png"),    
                                lat_min=40.846069,
                                lat_max=40.861034,
                                lon_min=-73.873620,    
                                lon_max=-73.831621)

    # Generate and save calendar and dumbbell plot with timestamp
    stravavis.plot_calendar.plot_calendar(activities, year_min=2015, year_max=2025, max_dist=50,
              fig_height=9, fig_width=15, output_file=os.path.join(output_dir, f"calendar_plot.png"))
    stravavis.plot_dumbbell.plot_dumbbell(activities, year_min=2015, year_max=2025, local_timezone='EST',
              fig_height=34, fig_width=34, output_file=os.path.join(output_dir, f"dumbbell_plot.png"))
    
    # Create the OpenSCAD file with timestamp
    skyline_progress_data = skyline.load_activity_data(activities_csv_path, min_date=min_date, max_date=max_date)
    skyline.create_skyline_with_text(skyline_progress_data, filename=os.path.join(output_dir, f"skyline.scad"))


if __name__ == "__main__":
    main()