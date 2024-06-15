from robocorp.tasks import task
from robocorp import browser

import shutil

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )

    download_orders_file()
    open_robot_order_website()
    close_annoying_modal()
    loop_orders()
    archive_receipts()
    clean_up()


def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_modal():
    """Clase constitutional rights modal"""
    page = browser.page()

    page.click("text=OK")

def order_another_robot():
    """click 'ORDER ANOTHER ROBOT' button"""
    page = browser.page()
    page.click("#order-another")

def preview_robot():
    """Click on the 'Preview' button"""
    page = browser.page()
    page.click("text=Preview")  

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Adds the screenshot to the PDF"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot,
                                   source_path= pdf_file,
                                   output_path = pdf_file)

def screenshot_robot(order_number):
    """Taking an informative screenshot about our robot ordered"""
    page = browser.page()
    file_name = "output/screenshots/" + order_number + ".png"
    page.screenshot(path=file_name)
    return file_name


def get_text_from_badge_success():
    """Obtiene el texto de un elemento con la clase 'badge badge-success'"""
    page = browser.page()

    try:
        receipt_number = page.locator("#receipt > p.badge.badge-success")
        print(receipt_number.inner_text())
        order_number = receipt_number.inner_text()
    except Exception:
        print(Exception)
        page.click("#order")
        
        element_exists = page.query_selector("#receipt > p.badge.badge-success")
        if element_exists:
            receipt_number = page.locator("#receipt > p.badge.badge-success")
        else:
            page.click("#order")
            receipt_number = page.locator("#receipt > p.badge.badge-success")

        print(receipt_number.inner_text())
        order_number = receipt_number.inner_text()

    return order_number


def store_receipt_as_pdf(order_number):
    """Export the order to a PDF file"""
    page = browser.page()
    order_results_html = page.locator("#receipt").inner_html()

    file_name = "output/receipts/" + order_number + ".pdf"

    pdf = PDF()
    pdf.html_to_pdf(order_results_html, file_name)
    return file_name

def submit_order():
    """Submit the order when the data is full filled"""
    page = browser.page()

    page.click("#order")
    order_number = get_text_from_badge_success()
    pdf_file = store_receipt_as_pdf(order_number)
    screenshot = screenshot_robot(order_number)
    embed_screenshot_to_receipt(screenshot, pdf_file)
    order_another_robot()
    close_annoying_modal()

def archive_receipts():
    """Archives all the receipt pdfs into a single zip archive"""
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")

def clean_up():
    """Cleans up the folders where receipts and screenshots are saved."""
    shutil.rmtree("./output/receipts")
    shutil.rmtree("./output/screenshots")       

def fill_the_form(order_rep):
    """Fills in the orders form and click the 'Order' button"""
    page = browser.page()

    page.select_option("#head", str(order_rep["Head"]))
    radio_button_value = order_rep["Body"]
    selector = f'input[type="radio"][value="{radio_button_value}"]'
    page.click(selector)
    selector = f'input[type=number]'
    page.fill(selector, str(order_rep["Legs"]))
    page.fill("#address", str(order_rep["Address"]))
    preview_robot()
    submit_order()



def download_orders_file():
    """Download excel file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def get_orders():
    """Get orders from CSV file and return the data"""
    table = Tables()
    order_table = table.read_table_from_csv("orders.csv", header=True)

    return order_table

def loop_orders():
    """Iterate each order into orders and send to fill orders form"""
    orders = get_orders()

    for order in orders:
        fill_the_form(order)





