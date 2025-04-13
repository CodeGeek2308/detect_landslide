import os
import time
from supabase import create_client
from PIL import Image, ImageChops
import requests
from io import BytesIO

# Initialize Supabase connection using environment variables
url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]
supabase = create_client(url, key)

# Function to download an image from Supabase storage
def download_image_from_supabase(filename):
    try:
        response = supabase.storage.from_("esp32-uploads").download(filename)
        image_data = response["data"]
        image = Image.open(BytesIO(image_data))
        return image
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

# Function to compare two images and detect changes (simple pixel difference)
def detect_landslide(image1, image2):
    # Convert both images to grayscale for better comparison
    image1 = image1.convert("L")
    image2 = image2.convert("L")

    # Compute the difference between the two images
    diff = ImageChops.difference(image1, image2)
    if diff.getbbox():  # If there's any difference in the images
        print("Landslide detected!")
        return True
    else:
        print("No landslide detected.")
        return False

# Main function to run the detection every 5 seconds
def run_landslide_detection():
    # Keep track of the last image to compare with
    last_image = None

    while True:
        # Timestamp for image filenames
        timestamp = time.strftime("%Y%m%d%H%M%S", time.gmtime())
        filename = f"image_{timestamp}.jpg"

        # Download the current image from Supabase storage
        current_image = download_image_from_supabase(filename)

        if current_image and last_image:
            # Compare the current image with the last image
            landslide_detected = detect_landslide(last_image, current_image)

            if landslide_detected:
                # Optionally, do something when a landslide is detected
                # For example, send an alert or save the result
                pass

        # Update the last image for the next comparison
        last_image = current_image

        # Wait for 5 seconds before checking again
        time.sleep(5)

# Run the detection
if __name__ == "__main__":
    run_landslide_detection()
