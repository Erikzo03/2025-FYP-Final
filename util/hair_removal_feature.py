import cv2
import numpy as np
import os
import shutil
from tqdm import tqdm

def remove_and_save_hairs(
    image_path,
    output_dir,
    blackhat_kernel_size=(15, 15),
    threshold_value=18,
    dilation_kernel_size=(3, 3),
    dilation_iterations=2,
    inpaint_radius=5,
    min_hair_contours_to_process=1,
    min_contour_area=5,            
):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(image_path)

    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Image not found at: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Morphological operations to detect hairs
    kernel_blackhat = cv2.getStructuringElement(cv2.MORPH_RECT, blackhat_kernel_size)
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel_blackhat)

    _, thresh = cv2.threshold(blackhat, threshold_value, 255, cv2.THRESH_BINARY)

    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, dilation_kernel_size)
    dilated_mask = cv2.dilate(thresh, kernel_dilate, iterations=dilation_iterations)

    # Calculate hair ratio based on the area of the dilated_mask
    total_image_pixels = gray.shape[0] * gray.shape[1]
    if total_image_pixels > 0:
        hair_mask_pixels = np.sum(dilated_mask == 255)  # Count white pixels in the binary mask
        hair_ratio = hair_mask_pixels / total_image_pixels
    else:

        hair_ratio = 0.0

    # Find contours to count individual hair structures for the decision logic
    contours, _ = cv2.findContours(dilated_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Filter contours by area to count only significant hair segments
    significant_contours = [c for c in contours if cv2.contourArea(c) > min_contour_area]
    hair_count = len(significant_contours) # Number of distinct hair objects considered significant

    output_path = os.path.join(output_dir, filename)

    # Decision to inpaint is based on the count of significant hair contours
    if hair_count < min_hair_contours_to_process:
        shutil.copy2(image_path, output_path)

        return hair_ratio, output_path, "No significant hairs found, original image copied."
    else:
        inpainted_image = cv2.inpaint(img, dilated_mask, inpaint_radius, cv2.INPAINT_TELEA)
        cv2.imwrite(output_path, inpainted_image)
        # Return the hair_ratio. The message still uses hair_count for specific information.
        return hair_ratio, output_path, f"{hair_count} hairs removed."


def process_folder(input_folder, output_folder="output_cleaned"):
    supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    os.makedirs(output_folder, exist_ok=True)

    print(f"Processing images from: {input_folder}")
    print(f"Saving results to: {output_folder}")
    print("-" * 40)

    params = {
        "blackhat_kernel_size": (15, 15),
        "threshold_value": 18,
        "dilation_kernel_size": (3, 3),
        "dilation_iterations": 2,
        "inpaint_radius": 5,
        "min_hair_contours_to_process": 1,
        "min_contour_area": 5
    }

    processed = 0
    skipped = 0
    errored = 0
    total = 0

    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(supported_extensions)]

    for filename in tqdm(image_files, desc="Hair Removal Standalone Processing"):
        total += 1
        image_path = os.path.join(input_folder, filename)

        try:
            returned_metric, out_path, msg = remove_and_save_hairs(
                image_path=image_path,
                output_dir=output_folder,
                **params
            )
            if "No significant hairs found" in msg:
                skipped += 1
            else:
                processed += 1
        except Exception as e:
            print(f"\n[ERROR] {filename}: {e}")
            errored += 1

    print("-" * 40)
    print(f"Total image files found: {total}")
    print(f"Images where inpainting was applied: {processed}")
    print(f"Images where original was copied (no/few hairs): {skipped}")
    print(f"Errors during processing: {errored}")

if __name__ == "__main__":
    input_folder = r"C:\Users\laura\Documents\University\2nd semester\Projects in Data Science\Projects\Final Project\matched_pairs\images"
    output_folder = r"C:\Users\laura\Documents\University\2nd semester\Projects in Data Science\Projects\Final Project\images after hair removal"

    os.makedirs(output_folder, exist_ok=True)

    # Delete previous hair-removed images to ensure a fresh run for testing
    if os.path.exists(output_folder):
        print(f"Deleting existing hair-removed images folder: {output_folder}")
        shutil.rmtree(output_folder)
        os.makedirs(output_folder, exist_ok=True)

    process_folder(input_folder, output_folder)