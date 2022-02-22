# aadhaar-ocr

## Requirements
1) opencv-python 4.5.3.56 or above
2) pytesseract 0.3.8 or above
3) spacy 3.2.1 or above
4) numpy 1.20.0 or above

## Downloading Tesseract OCR
Along with above requirements you also need Tesseract OCR Engine.

Download Tesseract OCR for windows
1) 32-bit version:
   https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w32-setup-v5.0.1.20220118.exe
2) 64-bit version:
   https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.0.1.20220118.exe

More info at https://github.com/UB-Mannheim/tesseract/wiki
Note: Download the file and extract the contents of the file. Keep a note of the path of tesseract.exe(Eg: Desktop\Tesseract\tesseract.exe)

## Project Info

Extract details like Name, Date of Birth, Gender, Mobile No., Aadhaar No., and Address directly from an image of Aadhaar Card using OCR.

### Code Explanation

Setting up path to tesseract.exe(tesseract.exe cant be found at download location of Tesseract OCR Engine Eg: Desktop\Tesseract\tesseract.exe),
aadhaar_front_img and aadhaar_back_img

### main.py
In main.py set the following paths
```
tesseract_path = Path("<path/to/tesseract.exe>") // set tesseract.exe path
aadhaar_front_img_path = Path("<path/to/aadhaar_front_image>") // set aadhaar front image path
aadhaar_back_img_path = Path("<path/to/aadhaar_back_image>") // set aadhaar back image path
pytesseract.pytesseract.tesseract_cmd = tesseract_path
```
After setting path you can tweak some optional values like fx,fy to resize the original image.
```
img = cv2.resize(img,(0,0),fx=0.5,fy=0.5)
// Resize image (fx=0.5,fy=0.5 is half the original size and fx=2,fy=2 is double the original size)
```
Now you can run main.py

### Running main.py
On running main.py you will get a black and white aadhaar front image first, here you will have to choose four points to crop the image so that we only keep data part of the image.

###The order of choosing the points is TopLeft=>TopRight=>BottomLeft=>BottomRight
The points are marked in red with their order(try to chose points similar to the image below, we only need that part of the image)
The four points need not form an exact rectangle it can form any quadrilateral because we perspective transform the image later on.

![alt text](https://github.com/wasdac9/aadhaar-ocr/blob/main/aadhaar_back_example.png)


