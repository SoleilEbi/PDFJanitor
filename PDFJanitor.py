import pymupdf
import ocrmypdf
import gc
import os
from io import BytesIO
from PIL import Image
from tqdm import tqdm
from pathlib import Path


ocr_global_permit = 0
"""ocr_global_permit manipulates if the warning
    about scanned pdf's will appear to the user.
    0 = The warning will keep appearing and asking for user input
    1 = The warning will stop appearing and will always activate
     ocr_pdf_creator
    2 = The warning will stop appearing and won't even do the check to scan
     pdf's"""


def cleaner(folder_path):
    global ocr_global_permit
    pdf = pymupdf.open(folder_path)
    path, extension = os.path.splitext(pdf.name)
    if (ocr_global_permit != 2):
        while True:
            keep_looping, ocr_global_permit, pdf = ocr_user_input_loop(
                ocr_global_permit, pdf, path, extension)

            if (keep_looping is False):
                break

    print("Analysing ", pdf.name)
    for page_num in tqdm(range(len(pdf))):

        page = pdf[page_num]
        image_list = page.get_images()
        for img_info in image_list:
            xref = img_info[0]
            page_object = pdf.extract_image(xref)

            img_file = BytesIO(page_object["image"])
            img = Image.open(img_file)

            width = img.size[0]
            height = img.size[1]

            new_width = int(width/2)
            new_height = int(height/2)

            resized_img = img.resize((new_width, new_height))

            output_buffer = BytesIO()
            resized_img.save(output_buffer, format="JPEG",
                             quality=60, optimize=True)
            compressed_bytes = output_buffer.getvalue()

            page.replace_image(xref, stream=compressed_bytes)
        gc.collect()

    pdf.save(path + "_optimized" + extension,
             garbage=4, deflate=True)


def is_scanned(pdf):
    scanned_pages = 0
    digital_pages = 0
    for pdf_pages in range(min(10, len(pdf))):
        page = pdf[pdf_pages]
        if (len(page.get_text().strip()) <= 30
                and len(page.get_images()) > 0):
            scanned_pages += 1
        else:
            digital_pages += 1

    if scanned_pages > digital_pages:
        return True

    return False


def ocr_pdf_creator(pdf, path, ext):
    total_pages = len(pdf)

    if (total_pages > 100):
        return ocr_split_merge(total_pages, pdf, path, ext)

    pdf.close()
    ocrmypdf.ocr(path + ext, path + "_ocr" + ext, deskew=True, jobs=2)
    return pymupdf.open(path + "_ocr" + ext)


def ocr_split_merge(total_pages, pdf, path, ext):
    chunk_size = 50
    temp_file = 0
    temp_file_total = 0
    for start_page in range(0,  total_pages, chunk_size):
        chunk_pdf = pymupdf.open()
        chunk_pdf.insert_pdf(pdf, from_page=start_page, to_page=min(
            start_page + chunk_size - 1, total_pages-1))
        chunk_pdf.save(path+"_temp_"+str(temp_file)+ext)
        temp_file += 1
        chunk_pdf.close()

    temp_file_total = temp_file
    temp_file = 0
    merged_ocr = pymupdf.open()

    for temp_file in range(temp_file_total):
        end_path = path+"_temp_"+str(temp_file)+"_ocr"+ext
        ocrmypdf.ocr(path+"_temp_"+str(temp_file)+ext,
                     path+"_temp_"+str(temp_file)+"_ocr"+ext)
        os.remove(path+"_temp_"+str(temp_file)+ext)
        chunk_ocr_pdf = pymupdf.open(end_path)
        merged_ocr.insert_pdf(chunk_ocr_pdf)
        chunk_ocr_pdf.close()
        os.remove(end_path)

    pdf.close()
    merged_ocr.save(path+"_ocr"+ext)
    return pymupdf.open(path+"_ocr"+ext)


def ocr_user_input_loop(global_permit, pdf, path, extension):

    print("Checking if PDF is scanned")
    if (is_scanned(pdf) and global_permit != 1):

        while True:
            print("This is PDF probably is Scanned."
                  " Would you like to do an OCR (Optical Character"
                  " Recognized)"
                  " Version before compression for better optimization?"
                  " (Y/N/All/None)")
            ocr_user_input = input()

            ocr_user_input = ocr_user_input.lower()

            if (ocr_user_input == "y"
                or ocr_user_input == "ye"
                    or ocr_user_input == "yes"
                    or ocr_user_input == "all"):

                if (ocr_user_input == "all"):
                    print("Are you sure? (Type: yes)")
                    ocr_user_input = input()
                    ocr_user_input = ocr_user_input.lower()
                    if (ocr_user_input == "yes"):
                        global_permit = 1
                    else:
                        continue

                pdf = ocr_pdf_creator(pdf, path, extension)
                return False, global_permit, pdf

            elif (ocr_user_input == "none"):
                print("Are you sure? (Type: yes)")
                ocr_user_input = input()
                ocr_user_input = ocr_user_input.lower()
                if (ocr_user_input == "yes"):
                    global_permit = 2
                    return False, global_permit, pdf
                else:
                    continue

            elif (ocr_user_input == "n"
                    or ocr_user_input == "no"):
                return False, global_permit, pdf
            else:
                print("Please, type again your answer")

    elif (is_scanned(pdf) and global_permit == 1):
        pdf = ocr_pdf_creator(pdf, path, extension)
        return False, global_permit, pdf

    else:
        return False, global_permit, pdf


def batch_folder_processes(target_path):
    path_obj = Path(target_path)
    print(f"Scanning folder '{target_path}' for PDF's...")
    pdf_files = list(path_obj.glob("**/*.pdf"))

    if not pdf_files:
        print("There are no PDF's on this directory")
        return

    print(f"Found {len(pdf_files)} PDF(s). starting batch")
    for pdf_file in pdf_files:
        cleaner(pdf_file)


if __name__ == "__main__":
    print("Welcome to PDFJanitor!")
    user_input = "Starting Value"
    while (True):
        while (True):
            print("Insert here a single pdf or folder you want to clean:")
            user_input = input()

            desired_path = Path(user_input)

            if (desired_path.exists()):
                batch_folder_processes(desired_path)
                break
            else:
                print("The Path inserted is invalid")

        while (True):
            print("Do you want to repeat the process for another batch? (Y/N)")
            user_input = input()
            user_input = user_input.lower()
            break
        if (user_input == "y"
           or user_input == "ye"
           or user_input == "yes"):
            continue

        break
