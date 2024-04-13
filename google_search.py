from serpapi import GoogleSearch
from dotenv import load_dotenv
from datetime import datetime, timedelta
import csv
import os

# we hid the api key, so we need to grab it from the env file
load_dotenv("api_keys.env")
api_key = os.getenv("SERPAPI_GOOGLE_SEARCH_KEY")

<<<<<<< HEAD
<<<<<<< HEAD
# allow to query based on specific params
def calc_date(start_date):
    input_date = datetime.strptime(start_date, "%m/%d/%y")

    # calculations, 2 days before, 3 weeks after
    two_days_before = input_date - timedelta(days=2)
    three_weeks_after = input_date + timedelta(days=21)
    
    return two_days_before.strftime("%m/%d/%y"), three_weeks_after.strftime("%m/%d/%y")

def parse_csv(input_csv):
    columns = ["arrestdate", "CountyName", "ST"]  # columns where we want to select the data from
    data = []
    try:
        with open(input_csv, newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            header = next(csv_reader)
            
            column_indices = [header.index(col) for col in columns if col in header]
            for row in csv_reader:  # each row with have 3 items: "arrestdate", "CountyName", "ST"
                data.append([row[i] for i in column_indices])
    
    except Exception as e:
        print(f"Error processing CSV file: {e}")  # if the input csv is not valid

    return data

# helper function that will do all the searching and writing into the output csv file
def helper(query, start, end, csv_path):
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "google_domain": "google.com",
        "gl": "us",
        "hl": "en",
        "tbs": f"cdr:1,cd_min:{start},cd_max:{end}", # specific time search parameter
        "sort": "date"
    }
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        organic_results = results.get("organic_results", [])
        print(f"Results found: {len(organic_results)}")  # debugging line

        # Open the file with 'a' to append to the existing content
        with open(csv_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["Query", "Title", "Link", "Date"])
            for result in organic_results:
                writer.writerow({
                    "Query": query,
                    "Title": result.get("title", "N/A"),
                    "Link": result.get("link", "N/A"),
                    "Date": result.get("date", "N/A")
                })
    except Exception as e:
        print(f"Error during search or file writing: {e}")

def search_and_export(data):
    # Get the path to the desktop directory
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    # Define the full path to the CSV file on the desktop
    output_csv = os.path.join(desktop_path, "organic_results.csv")

    # check if the file exists, otherwise create and write the header
    if not os.path.exists(output_csv):
        with open(output_csv, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["Query", "Title", "Link", "Date"])
            writer.writeheader()

    # Process each query and append results to the CSV
    i = 0  # limit counter for testing
    for arrestdate, county, state in data:
        if i == 1: break  # limit counter for testing
        # print(arrestdate)  # for debugging

        start_date, end_date = calc_date(arrestdate)
        print(start_date, end_date, county, state)

        query1 = f"Immigration Raids, {county}, {state}, {start_date}"
        query2 = f"Immigration Raids, {county}, {state}, {end_date}"
        print(query1, query2)
        helper(query1, start_date, output_csv)
        helper(query2, end_date, output_csv)
        
        i += 1 # limit counter for testing
=======
=======
>>>>>>> 01b12fa53c01e5aaf35331f731b69decd92cf08e
# allow users to query based on specific params
search_query = input("Enter your search query: ")
start_date = input("Enter the start date (format m/d/yyyy): ")
end_date = input("Enter the end date (format m/d/yyyy): ")
date_range = f"{start_date}-{end_date}"

# search params for query
params = {
  "engine": "google",
  "q": search_query,
  "api_key": api_key,
  "google_domain": "google.com",
  "gl": "us",
  "hl": "en",
  "tbs": f"cdr:1,cd_min:{start_date},cd_max:{end_date}", # specific time search param
  "sort": "date"
}

# create a GoogleSearch object with the parameters
search = GoogleSearch(params)

# store the search results as a dictionary
results = search.get_dict()

# get the organic search results
organic_results = results["organic_results"]

# print the organic search results, what the csv file will show
for result in organic_results:
    print(result['title'], "-", result['link'])

def export_to_csv(organic_results, filename, search_params):
    """
    Export organic search results to a CSV file, including the publication date and search parameters.

    Parameters:
        organic_results (list): List of dictionaries containing organic search results.
        filename (str): Name of the CSV file to export the results to.
        search_params (dict): Dictionary containing the search parameters.
    """
    # Get the path to the desktop directory
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    # Define the full path to the CSV file on the desktop
    file_path = os.path.join(desktop_path, filename)

    # open the csv file to write it
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)  # instanstiate a writer

        # list out search parameters at the top
        writer.writerow(['Search Query Parameters'])
        for key, value in search_params.items():
            writer.writerow([key, value])
        writer.writerow([])

        # writing the search results
        fieldnames = ["Title", "Link", "Date"] # these are the files we will track
        dict_writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # write the header row for search results
        dict_writer.writeheader(fieldnames)

        # add each organic search result as a row in the CSV file, format it
        for result in organic_results:
            dict_writer.writerow({
                "Title": result.get("title", " "),
                "Link": result.get("link", ""),
                "Date": result.get("date", "N/A")  # date of publication date if available
            })

    print(f"Organic search results have been exported to {file_path}")
>>>>>>> 01b12fa53c01e5aaf35331f731b69decd92cf08e

def main():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    input_csv = os.path.join(desktop_path, "abnormal_arrest_dates.csv")
    data = parse_csv(input_csv)
    search_and_export(data)
    print(f"Organic search results have been exported to {os.path.join(desktop_path, 'organic_results.csv')}")

main()