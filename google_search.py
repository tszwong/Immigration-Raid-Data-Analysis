from serpapi import GoogleSearch
from dotenv import load_dotenv
import csv
import os

# we hid the api key, so we need to grab it from the env file
load_dotenv("api_keys.env")
api_key = os.getenv("SERPAPI_GOOGLE_SEARCH_KEY")

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


export_to_csv(organic_results, "organic_results.csv", params)
