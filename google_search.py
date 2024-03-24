from serpapi import GoogleSearch
from dotenv import load_dotenv
import csv
import os

load_dotenv()
api_key = os.getenv("SERPAPI_GOOGLE_SEARCH_KEY")

# Prompt the user for search query and date range
search_query = input("Enter your search query: ")
start_date = input("Enter the start date (format m/d/yyyy): ")
end_date = input("Enter the end date (format m/d/yyyy): ")
date_range = f"{start_date}-{end_date}"

# Set up the search parameters with user inputs
params = {
  "engine": "google",
  "q": search_query,
  "api_key": api_key,
  "google_domain": "google.com",
  "gl": "us",
  "hl": "en",
  "date_range": date_range
}

# Create a GoogleSearch object with the parameters
search = GoogleSearch(params)

# Get the search results as a dictionary
results = search.get_dict()

# Extract the organic search results
organic_results = results["organic_results"]

# Print the organic search results
for result in organic_results:
    print(result['title'], "-", result['link'])

def export_to_csv(organic_results, filename):
    """
    Export organic search results to a CSV file.

    Parameters:
        organic_results (list): List of dictionaries containing organic search results.
        filename (str): Name of the CSV file to export the results to.
    """
    # Get the path to the desktop directory
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    
    # Define the full path to the CSV file on the desktop
    file_path = os.path.join(desktop_path, filename)

    # Define the field names for the CSV file
    fieldnames = ["Title", "Link"]

    # Write the organic search results to the CSV file
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write the header row
        writer.writeheader()

        # Write each organic search result as a row in the CSV file
        for result in organic_results:
            writer.writerow({"Title": result.get("title", " "), "Link": result.get("link", "")})

    print(f"Organic search results have been exported to {file_path}")

export_to_csv(organic_results, "organic_results.csv")
