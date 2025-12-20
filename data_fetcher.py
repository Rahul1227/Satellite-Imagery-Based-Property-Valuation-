"""
data_fetcher.py

Script for downloading satellite images using Mapbox API.
This module fetches satellite imagery for properties based on their latitude and longitude coordinates.

Author: [Your Name]
Date: December 2024
Project: Satellite Imagery-Based Property Valuation
"""

import requests
from PIL import Image
from io import BytesIO
import pandas as pd
import os
import time
from src.config import MAPBOX_API_TOKEN



class SatelliteImageFetcher:
    """
    A class for downloading satellite images from Mapbox Static Images API.
    
    This class handles the process of fetching satellite imagery for properties
    using their geographic coordinates and saving them locally.
    """
    
    def __init__(self, api_token, image_size='256x256', zoom_level=18):
        """
        Initializing the satellite image fetcher.
        
        Parameters:
            api_token (str): Mapbox API access token
            image_size (str): Dimensions of the downloaded images (default: '256x256')
            zoom_level (int): Zoom level for satellite imagery (default: 18)
        """
        self.api_token = api_token
        self.base_url = 'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static'
        self.image_size = image_size
        self.zoom_level = zoom_level
        
        print("Satellite Image Fetcher initialized successfully")
        print(f"Configuration - Image size: {image_size}, Zoom level: {zoom_level}")
    
    
    def download_single_image(self, latitude, longitude, property_id, save_path):
        """
        Downloading a single satellite image for a specific property.
        
        Parameters:
            latitude (float): Latitude coordinate of the property
            longitude (float): Longitude coordinate of the property
            property_id (int/str): Unique identifier for the property
            save_path (str): Complete file path where the image will be saved
            
        Returns:
            bool: True if download was successful, False otherwise
        """
        try:
            # Building the API request URL with coordinates and parameters
            api_url = f"{self.base_url}/{longitude},{latitude},{self.zoom_level}/{self.image_size}"
            api_url += f"?access_token={self.api_token}"
            
            # Sending GET request to Mapbox API
            response = requests.get(api_url, timeout=10)
            
            # Checking if the request was successful
            if response.status_code == 200:
                # Opening the image from response content
                img = Image.open(BytesIO(response.content))
                
                # Saving the image to the specified path
                img.save(save_path, 'JPEG', quality=95)
                
                return True
            else:
                print(f"Download failed for property {property_id}: HTTP Status {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"Request timeout for property {property_id}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"Network error for property {property_id}: {str(e)}")
            return False
        except Exception as e:
            print(f"Unexpected error for property {property_id}: {str(e)}")
            return False
    
    
    def download_images_for_dataset(self, data_df, save_folder, delay=0.2, progress_interval=50):
        """
        Downloading satellite images for all properties in a dataset.
        
        This method iterates through a dataframe of properties and downloads
        satellite images for each one based on their coordinates.
        
        Parameters:
            data_df (pd.DataFrame): DataFrame containing property data with 'id', 'lat', 'long' columns
            save_folder (str): Directory path where images will be saved
            delay (float): Delay between API requests in seconds (default: 0.2)
            progress_interval (int): Number of downloads between progress updates (default: 50)
            
        Returns:
            dict: Dictionary containing download statistics including:
                  - total: Total number of properties
                  - successful: Number of successful downloads
                  - failed: Number of failed downloads
                  - failed_ids: List of property IDs that failed
                  - total_time: Total time taken in seconds
                  - success_rate: Percentage of successful downloads
        """
        # Creating the save folder if it does not exist
        os.makedirs(save_folder, exist_ok=True)
        
        # Initializing counters for tracking download progress
        total_properties = len(data_df)
        successful_count = 0
        failed_count = 0
        failed_property_ids = []
        
        print("=" * 70)
        print(f"Starting download process for {total_properties} properties")
        print(f"Save location: {save_folder}")
        print("=" * 70)
        
        # Recording the start time for performance measurement
        start_time = time.time()
        
        # Iterating through each property in the dataframe
        for idx, row in data_df.iterrows():
            prop_id = row['id']
            lat = row['lat']
            lon = row['long']
            
            # Constructing the file path for saving the image
            image_file_path = os.path.join(save_folder, f'property_{prop_id}.jpg')
            
            # Checking if the image already exists to avoid re-downloading
            if os.path.exists(image_file_path):
                successful_count += 1
                continue
            
            # Attempting to download the image
            download_success = self.download_single_image(lat, lon, prop_id, image_file_path)
            
            # Updating the success/failure counters
            if download_success:
                successful_count += 1
            else:
                failed_count += 1
                failed_property_ids.append(prop_id)
            
            # Displaying progress updates at regular intervals
            if (idx + 1) % progress_interval == 0:
                elapsed_time = time.time() - start_time
                progress_percentage = ((idx + 1) / total_properties) * 100
                avg_time = elapsed_time / (idx + 1)
                estimated_remaining = avg_time * (total_properties - idx - 1)
                
                print(f"Progress: {idx + 1}/{total_properties} ({progress_percentage:.1f}%)")
                print(f"  Time elapsed: {elapsed_time/60:.1f} minutes")
                print(f"  Estimated remaining: {estimated_remaining/60:.1f} minutes")
            
            # Adding a delay between requests to respect API rate limits
            time.sleep(delay)
        
        # Calculating final statistics after all downloads complete
        total_elapsed_time = time.time() - start_time
        success_percentage = (successful_count / total_properties) * 100
        
        # Displaying the final summary
        print("\n" + "=" * 70)
        print("DOWNLOAD SUMMARY")
        print("=" * 70)
        print(f"Total properties processed: {total_properties}")
        print(f"Successful downloads: {successful_count} ({success_percentage:.1f}%)")
        print(f"Failed downloads: {failed_count}")
        print(f"Total time taken: {total_elapsed_time/60:.2f} minutes")
        print(f"Average time per image: {total_elapsed_time/total_properties:.2f} seconds")
        print("=" * 70)
        
        # Returning comprehensive statistics as a dictionary
        return {
            'total': total_properties,
            'successful': successful_count,
            'failed': failed_count,
            'failed_ids': failed_property_ids,
            'total_time': total_elapsed_time,
            'success_rate': success_percentage
        }
    
    
    def create_image_mapping(self, data_df, images_folder, output_csv_path):
        """
        Creating a CSV file that maps property IDs to their image file paths.
        
        This method generates a mapping file that connects each property ID
        to its corresponding satellite image file path.
        
        Parameters:
            data_df (pd.DataFrame): DataFrame containing property data
            images_folder (str): Folder where images are stored
            output_csv_path (str): Path where the mapping CSV file will be saved
            
        Returns:
            pd.DataFrame: DataFrame containing the image mapping information
        """
        print("Creating image mapping file...")
        
        # Creating a new dataframe with essential columns
        mapping_df = data_df[['id', 'lat', 'long']].copy()
        
        # Adding the image path column based on property ID
        mapping_df['image_path'] = mapping_df['id'].apply(
            lambda x: os.path.join(images_folder, f'property_{x}.jpg')
        )
        
        # Checking which images actually exist on disk
        mapping_df['image_exists'] = mapping_df['image_path'].apply(
            lambda x: os.path.exists(x)
        )
        
        # Saving the mapping to a CSV file
        mapping_df.to_csv(output_csv_path, index=False)
        
        # Calculating and displaying summary statistics
        existing_images = mapping_df['image_exists'].sum()
        total_images = len(mapping_df)
        
        print(f"Image mapping created successfully")
        print(f"Images available: {existing_images} out of {total_images}")
        print(f"Mapping saved to: {output_csv_path}")
        
        return mapping_df
    
    
    def verify_images(self, images_folder, sample_size=20):
        """
        Verifying the integrity of downloaded images.
        
        This method checks a sample of downloaded images to ensure they are
        not corrupted and can be opened properly.
        
        Parameters:
            images_folder (str): Folder containing the downloaded images
            sample_size (int): Number of images to verify (default: 20)
            
        Returns:
            dict: Dictionary with verification results including:
                  - total_checked: Number of images checked
                  - valid_images: Number of valid images
                  - corrupted_images: Number of corrupted images
        """
        print("Verifying downloaded images...")
        
        # Getting list of all image files in the folder
        image_files = [f for f in os.listdir(images_folder) if f.endswith('.jpg')]
        
        if len(image_files) == 0:
            print("No images found in the specified folder")
            return {'total_checked': 0, 'valid_images': 0, 'corrupted_images': 0}
        
        # Limiting the sample size to available images
        sample_size = min(sample_size, len(image_files))
        
        valid_count = 0
        corrupted_count = 0
        
        # Checking each image in the sample
        for img_file in image_files[:sample_size]:
            img_path = os.path.join(images_folder, img_file)
            try:
                # Attempting to open and verify the image
                img = Image.open(img_path)
                img.verify()
                valid_count += 1
            except Exception as e:
                print(f"Corrupted image found: {img_file}")
                corrupted_count += 1
        
        print(f"Verification complete: {valid_count} valid, {corrupted_count} corrupted")
        
        return {
            'total_checked': sample_size,
            'valid_images': valid_count,
            'corrupted_images': corrupted_count
        }


def main():
    """
    Main function demonstrating how to use the SatelliteImageFetcher class.
    
    This function serves as an example of how to:
    1. Initialize the image fetcher with API token
    2. Load property data
    3. Download images for properties
    4. Create image mapping files
    5. Verify downloaded images
    """
    
    # IMPORTANT: Replace with your actual Mapbox token
    # You can store this in a separate config file or environment variable
    MAPBOX_API_TOKEN = 'YOUR_MAPBOX_TOKEN_HERE'
    
    # Setting up file paths
    # Adjust these paths according to your Google Drive structure
    base_path = '/content/drive/My Drive/Property_Valuation_Project'
    data_path = f'{base_path}/data'
    images_path = f'{base_path}/images'
    
    # Defining paths for train and test images
    train_images_folder = f'{images_path}/train'
    test_images_folder = f'{images_path}/test'
    
    try:
        # Loading the training data
        print("Loading training data...")
        train_df = pd.read_csv(f'{data_path}/cleaned_train.csv')
        print(f"Loaded {len(train_df)} training properties")
        
        # Initializing the image fetcher
        fetcher = SatelliteImageFetcher(
            api_token=MAPBOX_API_TOKEN,
            image_size='256x256',
            zoom_level=18
        )
        
        # Downloading images for training data
        print("\nDownloading training images...")
        train_stats = fetcher.download_images_for_dataset(
            data_df=train_df,
            save_folder=train_images_folder,
            delay=0.2,
            progress_interval=50
        )
        
        # Creating image mapping for training data
        print("\nCreating training image mapping...")
        train_mapping = fetcher.create_image_mapping(
            data_df=train_df,
            images_folder=train_images_folder,
            output_csv_path=f'{data_path}/train_image_mapping.csv'
        )
        
        # Verifying downloaded training images
        print("\nVerifying training images...")
        train_verification = fetcher.verify_images(
            images_folder=train_images_folder,
            sample_size=20
        )
        
        # Loading and processing test data if available
        try:
            print("\nLoading test data...")
            test_df = pd.read_excel(f'{data_path}/test2.xlsx')
            print(f"Loaded {len(test_df)} test properties")
            
            # Downloading images for test data
            print("\nDownloading test images...")
            test_stats = fetcher.download_images_for_dataset(
                data_df=test_df,
                save_folder=test_images_folder,
                delay=0.2,
                progress_interval=20
            )
            
            # Creating image mapping for test data
            print("\nCreating test image mapping...")
            test_mapping = fetcher.create_image_mapping(
                data_df=test_df,
                images_folder=test_images_folder,
                output_csv_path=f'{data_path}/test_image_mapping.csv'
            )
            
            print("\nAll images downloaded and mapped successfully")
            
        except FileNotFoundError:
            print("\nTest data file not found. Skipping test image download.")
        
    except Exception as e:
        print(f"\nError in main execution: {str(e)}")
        raise


if __name__ == "__main__":
    main()