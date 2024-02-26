
import pytesseract
import cv2
import re
import numpy as np

def enhance_image(image_path, image_path_download,color_correction_factor=1.5):
    img = cv2.imread(image_path) # Read the image
    color_corrected_img = np.clip(img * color_correction_factor, 0, 255).astype(np.uint8)      # Apply color correction
    cv2.imwrite(image_path_download, color_corrected_img)  # Save the enhanced image
    text = pytesseract.image_to_string(image_path_download)  # Or use 'thresh' if you applied thresholding
    text = re.sub(r'[^a-zA-Z0-9]', '', text)
    print(text)
    return color_corrected_img

image_path = 'CaptchaImg/26_02_2024_15_25_43.png'
image_path_download = 'CaptchaImg/enhanced_one.png'
enhanced_image = enhance_image(image_path,image_path_download)




# text = pytesseract.image_to_string(image_path)  # Or use 'thresh' if you applied thresholding
# text = re.sub(r'[^a-zA-Z0-9]', '', text)
# print(text)