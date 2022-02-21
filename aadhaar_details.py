import cv2
import spacy
import numpy as np
import pytesseract
import re, os, time, json
from pathlib import Path
four_points = []

# function for drawing circles at clicked position
def draw_circle(event,x,y,flags,img):
    global four_points
    # the order of clicking points is:
    # TopLeftPoint -> TopRightPoint -> BottomLeftPoint -> BottomRightPoint
    if event == cv2.EVENT_LBUTTONDOWN:
        four_points.append([x,y])
        # drawing circle at clicked point
        cv2.circle(img,(x,y),5,(255,0,0),-1)

       
def image_processing(img,address=False):
    global four_points
    #convert image to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ## make image copy for warp perspective
    img_copy = img.copy() 
    cv2.namedWindow('image')
    # set mouse callback which detects all mouse inputs
    cv2.setMouseCallback('image',draw_circle,img)
    while(len(four_points)!=4):
        cv2.imshow('image',img)
        if cv2.waitKey(20) & 0xFF == 27:
                break

    cv2.destroyAllWindows()
    #print(four_points)

    # warp perspective and adaptive thresholding
    four_points = np.float32(four_points)
    if address:
        dst_pts = np.float32([[0,0],[1500,0],[0,400],[1500,400]])
    else:
        dst_pts = np.float32([[0,0],[850,0],[0,550],[850,550]])
    matrix = cv2.getPerspectiveTransform(four_points,dst_pts)
    if address:
        result = cv2.warpPerspective(img_copy, matrix, (1500,400))
        thresh = cv2.adaptiveThreshold(result, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY_INV, 55, 17)
        
    else:
        result = cv2.warpPerspective(img_copy, matrix, (850,550))
        thresh = cv2.adaptiveThreshold(result, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY, 77, 17)
    
    if address:
        # erosion to make text thinner
        kernel = np.ones((3,2), np.uint8)
        thresh = cv2.erode(thresh, kernel, iterations=2)

    cv2.imshow("thresh",thresh)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return thresh

def get_address(img, address=True):
    global four_points
    four_points = []
    res_string_address = None
    
    thresh = image_processing(img,address)
    #print("Thresh",thresh.shape)
    img2str_config_name = "--psm 4 --oem 3"
    res_string_address = pytesseract.image_to_string(thresh,lang='eng',config=img2str_config_name)
    regex_address = res_string_address.replace("Address:","")
    regex_address = res_string_address.replace("Address :","")
    regex_address = os.linesep.join([s for s in res_string_address.splitlines() if s])
    return(regex_address)

def get_values(img):
    global four_points
    regex_name = None
    regex_gender = None
    regex_dob = None
    regex_mobile_number = None
    regex_aadhaar_number = None
    #Name Entity Recognition function
    NER = spacy.load("en_core_web_sm")
    
    thresh = image_processing(img)
    img2str_config_name = "--psm 4 --oem 3"
    res_string_name = pytesseract.image_to_string(thresh,lang='eng',config=img2str_config_name)
    name=NER(res_string_name)

    #extracting name
    for word in name.ents:
        if word.label_ == "PERSON":
            regex_name  = re.findall("[A-Z][a-z]+", word.text)
    if not regex_name:
        regex_name = re.findall("[A-Z][a-z]+", res_string_name)
    #print(res_string_name)

    #extracting information other than name
    img2str_config_else = "--psm 3 --oem 3"
    res_string_else = pytesseract.image_to_string(thresh,lang='eng',config=img2str_config_else)
    

    if not regex_name:
        regex_name = re.findall("[A-Z][a-z]+", res_string_else)
    #extracting gender
    regex_gender = re.findall("MALE|FEMALE|male|female|Male|Female", res_string_else)
    if regex_gender:
        regex_gender = regex_gender[0]
    #print(regex_gender)

    #extracting date of birth
    regex_dob = re.findall("\d\d/\d\d/\d\d\d\d", res_string_else)
    if regex_dob:
        regex_dob = regex_dob[0]
    #print("dob1",regex_dob)
    if not regex_dob:
        regex_dob = re.findall("(\d\d\d\d){1}", res_string_else)[0]
    #print("dob2",regex_dob)

    #extracting mobile no.
    regex_mobile_number = re.findall("\d\d\d\d\d\d\d\d\d\d",res_string_else)
    if regex_mobile_number:
        regex_mobile_number = regex_mobile_number[0]
    else:
        regex_mobile_number = None
    #print(regex_mobile_number)

    #extracting aadhaar number
    regex_aadhaar_number = re.findall("\d\d\d\d \d\d\d\d \d\d\d\d",res_string_else)
    if regex_aadhaar_number:
        regex_aadhaar_number = regex_aadhaar_number[0]
    #print(regex_aadhaar_number)

    return(regex_name,regex_gender,regex_dob,regex_mobile_number,regex_aadhaar_number)


def send_to_json(regex_name,regex_gender,regex_dob,regex_mobile_number,regex_aadhaar_number,regex_address):
    time_sec = str(time.time()).replace(".","_")
    json_string = {
        time_sec: {
            "name": regex_name,
            "gender": regex_gender,
            "dob": regex_dob,
            "mobile number": regex_mobile_number,
            "aadhaar number": regex_aadhaar_number,
            "address": regex_address,
            },
        }

    #set json file path
    aadhaar_info_path = f"aadhaar_info_{time_sec}.json"
    aadhaar_info = Path(aadhaar_info_path)

    with open(aadhaar_info,"a") as f:
        json.dump(json_string, f, indent=4)
        print("Success!,Sent to JSON")

    
