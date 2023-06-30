
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from pydicom import dcmread
from pydicom.filereader import read_dicomdir

from os import listdir
from os.path import isfile, join

import numpy as np
from PIL import Image

app = FastAPI()
app.mount("/images", StaticFiles(directory="images"), name="images")

def get_images(mypath):
    dcmfiles= []
    for dcm in [f for f in listdir(mypath) if isfile(join(mypath, f))]:
        dcmfiles.append(dcmread(f"{mypath}/{dcm}"))

    for dcm in dcmimages:
        # Extract the pixel data
        pixel_data = dcm.pixel_array

        # Check if the pixel data is signed
        if dcm.PixelRepresentation == 1:
            # Convert signed pixel data to unsigned
            pixel_data = pixel_data + np.min(pixel_data)
            pixel_data = pixel_data.astype(np.uint16)

        # Check if the pixel data is using a non-standard photometric interpretation
        if dcm.PhotometricInterpretation != "RGB":
            # Convert to grayscale
            pixel_data = pixel_data * int(dcm.RescaleSlope) + int(dcm.RescaleIntercept)
            pixel_data = pixel_data.astype(np.uint16)

        # Create a PIL Image object
        image = Image.fromarray(pixel_data)

        # Save the image as a PNG file
        image.save(f"images/{dcm.PatientID}.png")

get_images('dicom')

# TODO:
# Replace with template file for production
def render_content(filter=None):
    header = """
        <html>
            <head>
                <title>Some HTML in here</title>
            </head>
            <body>
        """
    footer = """
            </body>
        </html>
        """
    imlist = []
    for image in listdir('images'):
        img_tag = f'<img src="/images/{image}" width="200" /><span>{image.split(".")[0]}</span>'
        if filter and image.startswith(filter):
            body = img_tag
        else:
            body = ''.join(imlist)

    return header + body + footer


@app.get("/patients")
def list_patients():
    html_content = render_content()
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/patients/{patient_id}")
def show_patient(patient_id):
    html_content = render_content(patient_id)
    return HTMLResponse(content=html_content, status_code=200)


