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
        resized_img.save(output_buffer, format="JPEG")
        compressed_bytes = output_buffer.getvalue()

        page.replace_image(xref, stream=compressed_bytes)