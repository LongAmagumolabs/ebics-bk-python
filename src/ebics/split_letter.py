import PyPDF2

# Open the original PDF file
with open("./letter/ini_letter_cert.pdf", "rb") as pdf_file:
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    print(pdf_reader)

    # Loop through each page and create separate PDF files
    for page_number in range(len(pdf_reader.pages)):
        pdf_writer = PyPDF2.PdfWriter()
        pdf_writer.add_page(pdf_reader.pages[page_number])

        # Create a file name for the current page
        output_filename = f"letter/trang_{page_number + 1}.pdf"

        # Write the page to a separate file
        with open(output_filename, "wb") as output_file:
            pdf_writer.write(output_file)
