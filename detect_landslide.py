from supabase import create_client
import cv2
import numpy as np
import os
import io
from PIL import Image
import time

# Supabase credentials (hardcoded)
url = "https://xhlyzfuidcgaviwimyll.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhobHl6ZnVpZGNnYXZpd2lteWxsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM5MjQyNjMsImV4cCI6MjA1OTUwMDI2M30.GukI9P58O0K_tZhk99upaZ7Th5TT8HVHGGUirt17NEw"
supabase = create_client(url, key)

def get_latest_image_urls(bucket_name="esp32-uploads"):
    try:
        res = supabase.storage.from_(bucket_name).list()
        files = sorted(res, key=lambda x: x["name"], reverse=True)
        if len(files) < 2:
            print("⚠️ Not enough images to compare.")
            return None, None
        return files[0]['name'], files[1]['name']
    except Exception as e:
        print("Error fetching image list:", e)
        return None, None

def download_image(bucket, filename):
    try:
        image_bytes = supabase.storage.from_(bucket).download(filename)
        return Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        print(f"Error downloading {filename}:", e)
        return None

def compare_images(img1, img2, threshold=25):
    img1 = np.array(img1.resize((224, 224)).convert('L'))
    img2 = np.array(img2.resize((224, 224)).convert('L'))
    diff = cv2.absdiff(img1, img2)
    non_zero_count = np.count_nonzero(diff)
    print("🔍 Pixel difference:", non_zero_count)
    return non_zero_count > threshold

def main_loop(duration_minutes=5, interval_seconds=5):
    total_iterations = (duration_minutes * 60) // interval_seconds
    for i in range(total_iterations):
        print(f"\n🕒 Checking for landslide... (Attempt {i + 1})")
        f1, f2 = get_latest_image_urls()
        if f1 and f2:
            img1 = download_image("esp32-uploads", f1)
            img2 = download_image("esp32-uploads", f2)
            if img1 and img2:
                landslide = compare_images(img1, img2)
                print("🚨 Landslide Detected!" if landslide else "✅ No landslide.")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    main_loop()
