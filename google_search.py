from serpapi import GoogleSearch
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests
import openai
import csv
import os

# we hid the api key, so we need to grab it from the env file
load_dotenv("api_keys.env")
api_key = os.getenv("SERPAPI_GOOGLE_SEARCH_KEY")
open_ai_key = os.getenv("OPEN_AI_KEY")

# helper function for date calculates for google search param
def calc_date(start_date):
    input_date = datetime.strptime(start_date, "%m/%d/%Y")

    # calculations, 2 days before, 3 weeks after
    two_days_before = input_date - timedelta(days=2)
    three_weeks_after = input_date + timedelta(days=21)
    
    return two_days_before.strftime("%m/%d/%y"), three_weeks_after.strftime("%m/%d/%Y")

# helper function to parse the input csv and grab the desired column values
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
def helper(query, county, state, start, end, csv_path1, csv_path2, date):
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "google_domain": "google.com",
        "gl": "us",
        "hl": "en",
        "tbs": f"cdr:1,cd_min:{start},cd_max:{end}",  # advanced date search
        "num": 10,  # n-1 results shown for each query
        "sort": "date"
    }
    try:
        search = GoogleSearch(params)
        # print(search)  # for testing
        results = search.get_dict()
        # print(results)  # for testing
        organic_results = results.get("organic_results", [])
        print(f"Results found: {len(organic_results)}")  # debugging line, show how many links found for the query

        valid_results = [] # stores the links that passes the chatgpt analysis
        invalid_results = [] # # stores the links that does not pass the chatgpt analysis

        # iterate through all links from the query, scrape the text, send it over to gpt api to analyze
        for result in organic_results:
            link = result.get("link", "N/A")
            print(link)
            location = f"{county}, {state}"
            text = scrape_article_text(link) #
            # print(text)
            
            try:
                # Check if text is not None and its length, check if we need to cut down on the text due to gpt api limitations
                if text is not None and len(text) > 5000:
                    text = shorten_data(text)
                elif text is None:
                    # Log if no text was scraped
                    print(f"No text found at {link}")
                    text = ""  # Set text to an empty string to handle further processing safely
            except Exception as e:
                print(f"Error processing text from {link}: {e}")
                text = ""  # Set text to an empty string to ensure the remaining code can execute

            # check if the text of current link, add to appropriate csv files
            if analyze_with_chatgpt(text, county, location, date) == True:
                valid_results.append(result)
            else:
                invalid_results.append(result)

        # write the valid results csv file
        with open(csv_path1, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["County", "State", "Title", "Link", "Date"])
            for result in valid_results:
                writer.writerow({
                    # "Query": query,
                    "County": county,
                    "State": state,
                    "Title": result.get("title", "N/A"),
                    "Link": result.get("link", "N/A"),
                    "Date": result.get("date", "N/A")
                })

        # write the invalid results csv file
        with open(csv_path2, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["County", "State", "Title", "Link", "Date"])
            for result in invalid_results:
                writer.writerow({
                    # "Query": query,
                    "County": county,
                    "State": state,
                    "Title": result.get("title", "N/A"),
                    "Link": result.get("link", "N/A"),
                    "Date": result.get("date", "N/A")
                })

    except Exception as e:
        print(f"Error during search or file writing: {e}")

def search_and_export(data):
    # Get the path to the desktop directory
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    # Define the full path to the CSV files on the desktop
    output_csv1 = os.path.join(desktop_path, "valid_organic_results.csv")
    output_csv2 = os.path.join(desktop_path, "invalid_organic_results.csv")

    # check if the file exists, otherwise create and write the header
    if not os.path.exists(output_csv1):
        with open(output_csv1, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["County", "State", "Title", "Link", "Date"])
            writer.writeheader()

    if not os.path.exists(output_csv2):
        with open(output_csv2, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["County", "State", "Title", "Link", "Date"])
            writer.writeheader()

    # Process each query and append results to the CSV
    i = 0  # limit counter for testings
    for arrestdate, county, state in data:
        if i == 1: break  # limit counter for testing
        # print(arrestdate)  # for debugging

        # since the dates provided in csv are m/dd/yy we need to fix the year
        year = arrestdate[-2:]
        no_year = arrestdate[:-2]
        year = "20" + year
        arrestdate = no_year + year
        # print(arrestdate)  # for testing

        start_date, end_date = calc_date(arrestdate)
        # start_date, end_date = calc_date("2/10/2017")  # for testing
        # print(start_date, end_date, county, state)  # for testing

        # query = f"Immigration Raid/Arrest, Travis, TX"  # for testing
        # print(query)  # for testing
        # helper(query, "Travis", "TX", start_date, end_date, output_csv1, output_csv2, "2/10/2017")  # for testing

        query = f"Immigration Raid/Arrest, {county}, {state}"  # the query sent to the helper function
        helper(query, county, state, start_date, end_date, output_csv1, output_csv2, arrestdate)
        
        i += 1 # limit counter for testing

# helper function to reduce text from scraped results
def shorten_data(text):
    new_text = text[:38888]
    return new_text

# helper function to check validity of the links
def analyze_with_chatgpt(text, county, location, date):
    openai.api_key = open_ai_key
    print(date, location)

    # questions we ask gpt to check
    questions = [
        f"Does this text mention {location} or {county}? Explicitly say yes or no in the first word of your response along with your explanation.",
        "Is the text related to immigration raids/arrests? Explicitly say yes or no in the first word of your response along with your explanation.",
        f"Does this text mention the date and is it around the date of {date}? Explicitly say yes or no in the first word of your responsee along with your explanation.",
        "Does this text confirm that the raid was conducted by Immigration and Customs Enforcement? Explicitly say yes or no in the first word of your response along with your explanation."
    ]
        
    res = []
    for question in questions:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Analyze the provided text for specific information."},
                {"role": "user", "content": text},
                {"role": "user", "content": question}
            ]
        )
        print(question + ":")
        answer = response['choices'][0]['message']['content'].strip() # grab the response from gpt for the question
        words = answer.split()  # Split the response into words
        print(answer + "\n")  # for debugging
        if "no" in words[0].lower():  # chec the first word
            res.append(False)
    
    for item in res:
        if item == False:  # mark link as invalid if any of the gpt questions did not pass
            return False
    return True

# helper function to scrape text of links from google search api results
def scrape_article_text(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the main article text; the tag and class might change based on the website
        article_text = soup.get_text(separator=' ', strip=True)
        print(len(article_text))
        # print(article_text)

        return article_text
    
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

# main driver of the program
def main():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    input_csv = os.path.join(desktop_path, "abnormal_arrest_dates.csv")
    data = parse_csv(input_csv)
    search_and_export(data)
    print(f"Organic search results have been exported to {os.path.join(desktop_path, 'valid_organic_results.csv')}")
    print(f"Organic search results have been exported to {os.path.join(desktop_path, 'invalid_organic_results.csv')}")

main()