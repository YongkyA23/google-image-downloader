from googleapiclient.discovery import build
import requests
import os
import pandas as pd
import re
import time
from PIL import Image

# Google Custom Search API key and search engine ID
API_KEY = "YOUR_API_KEY"
SEARCH_ENGINE_ID = "YOUR_SEARCH_ENGINE_ID"

def load_downloaded_images(filename):
    downloaded_images = set()
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            for line in file:
                downloaded_images.add(line.strip())
    return downloaded_images

def save_downloaded_images(downloaded_images, filename):
    with open(filename, 'w') as file:
        for image_filename in downloaded_images:
            file.write(image_filename + '\n')

# Function to download images with error handling and retry
def download_images(query, num_images, directory, downloaded_images, min_width=800, min_height=800):
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
            
            # Download images
            for i, result in enumerate(search_results):
                image_url = result['link']
                image_filename = f"{sanitized_query}_{i}.jpg"
                if image_filename not in downloaded_images:
                    response = requests.get(image_url, stream=True)
                    
                    # Check image size
                    image = Image.open(response.raw)
                    width, height = image.size
                    if width >= min_width and height >= min_height:
                        with open(os.path.join(directory, image_filename), 'wb') as file:
                            file.write(response.content)
                        print(f"Downloaded image {i+1}/{num_images} for query: {query}")
                        downloaded_images.add(image_filename)  # Add filename to set of downloaded images
                    else:
                        print(f"Skipping image {i+1}/{num_images} for query: {query}. Image size too small.")
                else:
                    print(f"Skipping already downloaded image: {image_filename}")
            
            # Break the loop if download succeeds
            break
        except Exception as e:
            print(f"Error downloading image for query: {query}: {str(e)}")
            # Retry after a short delay
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
    grouped_queries = data.groupby('jenis')
    
    # Initialize set to store downloaded image filenames
    downloaded_images = load_downloaded_images('downloaded_images.txt')
    
    # Iterate through each group
    for jenis, group in grouped_queries:
        directory = os.path.join("downloaded_images", jenis)  # Directory based on 'jenis'
        num_images = 1  # Number of images to download (set to 1)
        
        # Create directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Iterate through queries in the group
        for index, row in group.iterrows():
            query = row['nama']  # Read query from 'nama' column
            
            # Download images
            download_images(query, num_images, directory, downloaded_images)
    
    # Save downloaded image filenames
    save_downloaded_images(downloaded_images, 'downloaded_images.txt')

# Example usage
if __name__ == "__main__":
    excel_file = "queries.xlsx"  # Path to Excel file
    process_images_from_excel(excel_file)
