from googleapiclient.discovery import build
import requests
import os
import pandas as pd
import re
import time
import json
import random
import csv

# Google Custom Search API key and search engine ID
API_KEY = "AIzaSyAMuJxG40253IMdVzBV3oZH5KSMS6yN824"
SEARCH_ENGINE_ID = "42645c67cc1574e4e"

# Function to download images with error handling and retry
# Function to download images with error handling and retry
def download_images(query, num_images, directory, log_filename):
    # Initialize list to store download log
    download_log = []
    
    # Sanitize query to remove invalid characters from filename
    sanitized_query = re.sub(r'[\\/*?:"<>|]', '', query)
    
    # Create directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Build the custom search service
    service = build("customsearch", "v1", developerKey=API_KEY)
    
    # Retry download until it succeeds or max attempts reached
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            # Perform Google image search
            search_results = service.cse().list(
                q=query,
                cx=SEARCH_ENGINE_ID,
                searchType='image',
                num=num_images
            ).execute().get('items', [])
            
            # Download images and log information
            for i, result in enumerate(search_results):
                image_url = result['link']
                image_filename = f"{sanitized_query}_{i}.jpg"
                
                # Check if image dimensions meet the minimum criteria
                if 'image' in result and 'width' in result['image'] and 'height' in result['image']:
                    width = result['image']['width']
                    height = result['image']['height']
                    if width >= 500 and height >= 500:
                        response = requests.get(image_url, stream=True)
                        if response.status_code == 200:
                            with open(os.path.join(directory, image_filename), 'wb') as file:
                                file.write(response.content)
                            print(f"Downloaded image {i+1}/{num_images} for query: {query}")
                            # Append query and image filename to download log
                            download_log.append({'query': query, 'filename': image_filename})
                        else:
                            print(f"Failed to download image {i+1}/{num_images} for query: {query} - HTTP status code: {response.status_code}")
                    else:
                        print(f"Skipping image {image_url} as it doesn't meet the minimum size criteria")
                
                # Introduce a delay of 5 seconds between each image download
                time.sleep(3)
            
            # Write download log to CSV file
            with open(log_filename, 'a', newline='') as csvfile:
                fieldnames = ['query', 'filename']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                # Write header only if the file is empty
                if os.stat(log_filename).st_size == 0:
                    writer.writeheader()
                writer.writerows(download_log)
            
            # Break the loop if download succeeds
            break
        except Exception as e:
            print(f"Error downloading image for query: {query}: {str(e)}")
            # Check if the error is due to rate limit exceeded
            if 'rateLimitExceeded' in str(e):
                # If rate limit exceeded, apply exponential backoff
                delay = 2 ** attempt + random.uniform(0, 1)  # Add some randomness to avoid synchronized retries
                print(f"Rate limit exceeded. Retrying after {delay} seconds.")
                time.sleep(delay)
            else:
                # For other errors, retry immediately
                if attempt < max_attempts - 1:
                    print("Retrying download...")
                    time.sleep(2)  # Wait for 2 seconds before retrying
                else:
                    print("Max retry attempts reached. Skipping this query.")
                    break  # Skip to the next query if max attempts reached

# Function to process images from Excel file
def process_images_from_excel(excel_file):
    # Read Excel file
    data = pd.read_excel(excel_file)
    
    # Group queries by 'jenis'
    grouped_queries = data.groupby('Jenis')
    
    # Iterate through each group
    for jenis, group in grouped_queries:
        directory = os.path.join("downloaded_images", jenis)  # Directory based on 'jenis'
        num_images = 1  # Number of images to download (set to 1)
        
        # Iterate through queries in the group
        for index, row in group.iterrows():
            query = row['Nama']  # Read query from 'nama' column
            
            # Download images
            log_filename = os.path.join(directory, f"{jenis}_log.csv")
            download_images(query, num_images, directory, log_filename)

# Example usage
if __name__ == "__main__":
    excel_file = "queries.xlsx"  # Path to Excel file
    process_images_from_excel(excel_file)
