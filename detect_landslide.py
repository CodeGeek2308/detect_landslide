from supabase import create_client
import cv2
import numpy as np
import os
import io
from PIL import Image

# Supabase credentials (from GitHub secrets)
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def get_latest_image_urls(bucket_name="esp32-uploads"):
    # Fetch the list of files from the storage
    res = supabase.storage.from_(bucket_name).list()
    
    if not res:
        print("No images found in the bucket.")
        return None, None
    
    # Sort files by name (assuming latest images have lexicographically larger names)
    files = sorted(res, key=lambda x: x["name"], reverse=True)
    
    # If there are not enough files to compare, return None
    if len(files) < 2:
        print("Not enough images for comparison.")
        return None, None
    
    return files[0]['name'], files[1]['name']

def download_image(bucket, filename):
    # Download image from Supabase storage
    try:
        image_bytes = supabase.storage.from_(bucket).download(filename)
        return Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        print(f"Error downloading image {filename}: {e}")
        return None

def compare_images(img1, img2, threshold=25):
    # Convert images to grayscale and resize to standard dimensions
    img1 = np.array(img1.resize((224, 224)).convert('L'))
    img2 = np.array(img2.resize((224, 224)).convert('L'))
    
    # Calculate absolute difference between images
    diff = cv2.absdiff(img1, img2)
    non_zero_count = np.count_nonzero(diff)
    print(f"Pixel difference count: {non_zero_count}")
    
    # If the number of changed pixels exceeds the threshold, we consider it as a landslide
    return non_zero_count > threshold

def main():
    # Get the names of the two latest images
    f1, f2 = get_latest_image_urls()
    
    if f1 and f2:
        # Download the images
        img1 = download_image("esp32-uploads", f1)
        img2 = download_image("esp32-uploads", f2)
        
        if img1 and img2:
            # Compare the two images to check for landslide
            landslide = compare_images(img1, img2)
            print("Landslide Detected!" if landslide else "No landslide.")
        else:
            print("Error in downloading one or both images.")
    else:
        print("Could not retrieve two images for comparison.")

if __name__ == "__main__":
    main()
