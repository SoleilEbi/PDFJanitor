import pymupdf
import ocrmypdf
from io import BytesIO
from PIL import Image
from tqdm import tqdm

"Getting Information about the pymupdf module"
print(pymupdf.__doc__)

"Opening pdf and getting the location and information of the image on the"
"first page"

"Extracting the image out of the PDF and storing on a Variable"


def cleaner(folder_path):
    pdf = pymupdf.open(folder_path)
    ocr_global_permit = 0
    """ocr_global_permit manipulates if the warning
    about scanned pdf's will appear to the user.
    0 = The warning will keep appearing and asking for user input
    1 = The warning will stop appearing and will always activate
     ocr_pdf_creator
    2 = The warning will stop appearing and won't even do the check to scan
     pdf's"""
    if (ocr_global_permit != 2 or ocr_global_permit != 1):
        while True:
            print("Checking if PDF is scanned")
            if (is_scanned(pdf)):

                print("This is PDF probably is Scanned."
                      " Would you like to do an OCR (Optical Character"
                      " Recognized)"
                      " Version before compression for better optimization?"
                      " (Y/N/All/None)")
                ocr_user_input = input()

                ocr_user_input = ocr_user_input.lower()

                if (ocr_user_input == "y"
                    or ocr_user_input == "ye"
                        or ocr_user_input == "yes"):
                    pdf = pymupdf.open(ocr_pdf_creator(pdf))

                elif (ocr_user_input == "all"):
                    print("Are you sure? (Type: yes)")
                    ocr_user_input = input()
                    ocr_user_input = ocr_user_input.lower()
                    if (ocr_user_input == "yes"):
                        ocr_global_permit = 1

                elif (ocr_user_input == "none"):
                    print("Are you sure? (Type: yes)")
                    ocr_user_input = input()
                    ocr_user_input = ocr_user_input.lower()
                    if (ocr_user_input == "yes"):
                        ocr_global_permit = 2

                elif (ocr_user_input == "n"
                      or ocr_user_input == "no"):
                    break
                else:
                    print("Please, type again your answer")

    elif (ocr_global_permit == 1):
        pdf = pymupdf.open(ocr_pdf_creator(pdf))

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
                             quality=50, optimize=True)
            compressed_bytes = output_buffer.getvalue()

            page.replace_image(xref, stream=compressed_bytes)

    pdf.save("Projetos/PDFJanitor/trial/optimized.pdf",
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


if __name__ == "__main__":
    cleaner("Projetos/PDFJanitor/trial/*.pdf")


def ocr_pdf_creator(pdf, name, path):
    pre_ocr_pdf = pdf
    pdf.close()
    return ocrmypdf.ocr(pre_ocr_pdf, deskew=True)
