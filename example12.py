import streamlit as st
from PIL import Image
import pytesseract
import re
import pandas as pd
import os
from datetime import datetime

def extract_aadhaar_info(text):
    aadhaar_pattern = r'\b\d{4}\s\d{4}\s\d{4}\b'
    gender_pattern = r'\b(?:Male|Female|M|F)\b'

    aadhaar_match = re.search(aadhaar_pattern, text)
    gender_match = re.search(gender_pattern, text, re.IGNORECASE)

    aadhaar_number = aadhaar_match.group() if aadhaar_match else None
    gender = gender_match.group() if gender_match else None
    
    return aadhaar_number, gender



def extract_pan_info(text):
    pan_pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'
    dob_pattern = r'\b\d{2}/\d{2}/\d{4}\b'
                                            
    pan_match = re.search(pan_pattern, text)
    dob_match = re.search(dob_pattern, text)

    pan_number = pan_match.group() if pan_match else None
    dob = dob_match.group() if dob_match else "None"

    return pan_number, dob, 

def save_to_csv(details, filename='data.csv'):
    df = pd.DataFrame([details])
    if os.path.exists(filename):
        df.to_csv(filename, mode='a', header=False, index=False)
    else:
        df.to_csv(filename, index=False)

def save_uploaded_file(uploaded_file, folder, filename):
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_path = os.path.join(folder, filename)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# Streamlit App
st.set_page_config(page_title="ABC Bank Credit Card Application", page_icon="🏦")

st.title("ABC Bank")
st.header("Apply for Credit Card")
st.write("""
Welcome to ABC Bank's online credit card application portal.
Please fill in your details and upload your Aadhaar and PAN card images to apply for a credit card.
""")

# Create a form
with st.form(key='upload_form'):
        
    name = st.text_input("Enter your name")
    mobile_number1 = st.text_input("Enter your Mobile Number")
    email = st.text_input("Enter your Email")
    pincode = st.text_input("Enter your Pincode")
    city = st.text_input("Enter your city")
    state = st.text_input("Enter your state")
    aadhaar_file = st.file_uploader("Upload your Aadhaar card", type=["jpg", "jpeg", "png"])
    pan_file = st.file_uploader("Upload your PAN card", type=["jpg", "jpeg", "png"])

    # Submit button
    submit_button = st.form_submit_button(label='Submit')

if submit_button:
    if mobile_number1 and email and city and state and pincode and name and aadhaar_file is not None and pan_file is not None:

        try:
            path = r"C:\Users\visha\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
            pytesseract.pytesseract.tesseract_cmd = path
            aadhaar_image = Image.open(aadhaar_file)
            aadhaar_text = pytesseract.image_to_string(aadhaar_image)
            aadhaar_number, gender = extract_aadhaar_info(aadhaar_text)

            if aadhaar_number:
                user_folder = os.path.join("user_data", aadhaar_number.replace(" ", ""))
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

                aadhaar_filename = f"Aadhaar_{timestamp}.png"
                aadhaar_path = save_uploaded_file(aadhaar_file, user_folder, aadhaar_filename)

                pan_image = Image.open(pan_file)
                pan_text = pytesseract.image_to_string(pan_image)
                pan_number, dob = extract_pan_info(pan_text)

                if pan_number and dob:# and name:
                    pan_filename = f"PAN_{timestamp}.png"
                    pan_path = save_uploaded_file(pan_file, user_folder, pan_filename)

                    details = {
                        'Name': name,
                        'Aadhaar Number': aadhaar_number,
                        'PAN Number': pan_number,
                        'Date of Birth': dob,
                        'Entered Mobile Number': mobile_number1,
                        'Gender': gender,                       
                        'Email': email,
                        'City' : city,
                        'state': state,
                        'Pincode': pincode
                    }
                    save_to_csv(details)
                    st.success("Details saved successfully!")
                else:
                    if not pan_number:
                        st.error("PAN Number not found")
                    if not dob:
                        st.error("Date of Birth not found")
                    if not name:
                        st.error("Name not found")
            else:
                st.error("Aadhaar Number not found")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please fill in all details and upload both Aadhaar and PAN card images.")
