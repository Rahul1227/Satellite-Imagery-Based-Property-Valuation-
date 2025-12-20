"""
data_fetcher.py
Script for downloading satellite images using Mapbox API.
"""

import requests
from PIL import Image
from io import BytesIO
import pandas as pd
import os
import time


class SatelliteImageFetcher:
    """Class for downloading satellite images from Mapbox Static Images API."""
    
    def __init__(self, api_token, image_size='256x256', zoom_level=18):
        """
        Initialize the satellite image fetcher.
        
        Parameters:
            api_token (str): Mapbox API access token
            image_size (str): Image dimensions (default: '256x256')
            zoom_level (int): Zoom level (default: 18)
        """
        self.api_token = api_token
        self.base_url = 'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static'
        self.image_size = image_size
        self.zoom_level = zoom_level
        
        print("Satellite Image Fetcher initialized successfully")
        print(f"Configuration - Image size: {image_size}, Zoom level: {zoom_level}")
    
    
    def download_single_image(self, latitude, longitude, property_id, save_path):
        """
        Download a single satellite image.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Building API URL
            api_url = f"{self.base_url}/{longitude},{latitude},{self.zoom_level}/{self.image_size}"
            api_url += f"?access_token={self.api_token}"
            
            # Sending request
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                # Saving image
                img = Image.open(BytesIO(response.content))
                img.save(save_path, 'JPEG', quality=95)
                return True
            else:
                print(f"Failed for property {property_id}: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error for property {property_id}: {str(e)}")
            return False
    
    
    def create_image_mapping(self, data_df, images_folder, output_csv_path):
        """
        Create CSV mapping property IDs to image file paths.
        
        Returns:
            pd.DataFrame: Mapping dataframe
        """
        print("Creating image mapping file...")
        
        # Creating mapping dataframe
        mapping_df = data_df[['id', 'lat', 'long']].copy()
        mapping_df['image_path'] = mapping_df['id'].apply(
            lambda x: os.path.join(images_folder, f'property_{x}.jpg')
        )
        mapping_df['image_exists'] = mapping_df['image_path'].apply(os.path.exists)
        
        # Saving to CSV
        mapping_df.to_csv(output_csv_path, index=False)
        
        existing_images = mapping_df['image_exists'].sum()
        print(f"Images available: {existing_images}/{len(mapping_df)}")
        print(f"Mapping saved to: {output_csv_path}")
        
        return mapping_df
    
    
    def verify_images(self, images_folder, sample_size=50):
        """
        Verify integrity of downloaded images.
        
        Returns:
            dict: Verification results
        """
        print("Verifying downloaded images...")
        
        image_files = [f for f in os.listdir(images_folder) if f.endswith('.jpg')]
        
        if len(image_files) == 0:
            print("No images found")
            return {'total_checked': 0, 'valid_images': 0, 'corrupted_images': 0}
        
        sample_size = min(sample_size, len(image_files))
        valid_count = 0
        corrupted_count = 0
        
        for img_file in image_files[:sample_size]:
            img_path = os.path.join(images_folder, img_file)
            try:
                img = Image.open(img_path)
                img.verify()
                valid_count += 1
            except:
                print(f"Corrupted: {img_file}")
                corrupted_count += 1
        
        print(f"Verification complete: {valid_count} valid, {corrupted_count} corrupted")
        
        return {
            'total_checked': sample_size,
            'valid_images': valid_count,
            'corrupted_images': corrupted_count
        }