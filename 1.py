from PIL import Image
import pytesseract

image_path = 'CaptchaImg/13_02_2024_11_14_29.png'
image = Image.open(image_path)

# Perform OCR on the image
text = pytesseract.image_to_str(image)

# Print the extracted text
print("Extracted Text:")
print(text)
