import pymupdf
from io import BytesIO
from PIL import Image
from tqdm import tqdm

"Getting Information about the pymupdf module"
print(pymupdf.__doc__)

"Opening pdf and getting the location and information of the image on the"
"first page"

"Extracting the image out of the PDF and storing on a Variable"

pdf = pymupdf.open("Projetos/PDFJanitor/trial/test.pdf")
print("Scanning ", pdf.name)


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

pdf.save("Projetos/PDFJanitor/trial/optimized.pdf", garbage=4, deflate=True)


def is_scanned(pdf):
    scanned_pages = 0
    digital_pages = 0
    for pdf_pages in range(10):
        page = pdf[pdf_pages]
        if (len(page.get_text().strip()) == 0
                and len(page.get_images()) > 0):
            scanned_pages += 1
        else:
            digital_pages += 1

    if scanned_pages >= 5 and digital_pages <= 5:
        return True
