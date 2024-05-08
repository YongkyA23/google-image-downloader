# Image Downloader from Google Custom Search API

This Python script allows you to download images from Google Custom Search API based on queries provided in an Excel file. It handles error handling, retries, and avoids re-downloading images that have already been downloaded.

## Features

- Downloads images from Google Custom Search API based on queries provided in an Excel file.
- Error handling and retries for robustness.
- Avoids re-downloading images that have already been downloaded.

## Requirements

- Python 3.x
- `google-api-python-client`
- `requests` 
- `pandas`

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/your_username/image-downloader.git
   ```

2. Navigate to the project directory:

   ```bash
   cd path_to_image_downloader
   ```

3. Install the required Python packages using pip:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Place your queries in an Excel file with two columns: "nama" for the query names and "jenis" for the query types.
2. Ensure your Google Custom Search API key and search engine ID are correctly configured in the script (`API_KEY` and `SEARCH_ENGINE_ID` variables).
3. Run the script:

   ```bash
   python image_downloader.py
   ```

4. The images will be downloaded into the `downloaded_images` directory, organized into subdirectories based on the query types.

## Example Excel File Format

| nama     | jenis    |
|----------|----------|
| cats     | animal   |
| dogs     | animal   |
| mountains| landscape|

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

Please let me know if you need further assistance!
