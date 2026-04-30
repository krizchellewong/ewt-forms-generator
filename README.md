# EWT Forms Generator

This project automates the process of:
1. Cleaning raw monthly withholding data
2. Aggregating it per company
3. Generating BIR EWT (Expanded Withholding Tax) forms as PDFs

All generated forms CANNOT BE EDITED. Any information that needs to be changed needs to be done so in the csv/xlsx files placed in the `input` folder. All generated files will be under the `output` folder. EWT forms will be generated in a folder labeled with their respective quarters. 

---

## Input Files

Prepare the following files in the `input` folder before execution.

### 1. `raw_data.xlsx`
- Contains **monthly sheets** for each quarter
- Each sheet represents one month (e.g., `January 2025`)
- Required columns per sheet:
  - `COMPANY_NAME`, `TIN`, `NET`

### 2. `company_info.csv`
- Contains a list of all companies, their addresses, and Alphanumeric Tax Code (ATC)
- Ensure that the TIN matches the TIN number of the desired comapny in `raw_data.xlsx`
- Required columns:
  - `COMPANY_NAME`, `TIN`, `ADDRESS`, `ZIP`, `ATC`

### 3. `payer_info.csv`
- Represents the payer (your company)
- Only **one row**
- Required columns: `NAME`, `TIN`, `ADDRESS`, `ZIP`


### 4. `coordinates.json`

Defines where values are placed in the PDF.

Includes:
- font settings
- TIN digit positions
- ZIP positions
- ATC position
- amount positions
- date fields

This file controls layout. Only configure this if the BIR form changes. 

### 5. `bir_form.pdf`

- Blank BIR EWT form template
- Used as the base for all generated PDFs

---

## File Paths Configuration

All file paths are defined as constants at the top of each script.

### In `scripts/read_data.py`:
COMPANY_INFO_FILE = "input/company_info.csv"
RAW_TAX_DATA = "input/raw_data.xlsx"

### In `scripts/generate_pdf.py`:
TEMPLATE_PDF = "input/bir_form.pdf"
CLEANED_FILE = "output/cleaned_data.csv"
PAYER_FILE = "input/payer_info.csv"
COORDINATES_FILE = "input/coordinates.json"


---

## Setup Instructions (Mac & Windows)

Follow these steps to run the project locally.

---

## 1. Install Python

- Download and install Python from: https://www.python.org/downloads/  
- During installation, enable **Add Python to PATH**  
- Verify installation in terminal: `python --version` or `python3 --version`

---

## 2. Install Dependencies

Run this in your project folder:

- Mac: `pip3 install openpyxl pypdf reportlab`  
- Windows: `pip install openpyxl pypdf reportlab`

---

## 3. Project Structure

Your folder should look like:

- `EWT-FORMS/`
  - `input/`
  - `output/`
  - `scripts/`
  - `main.py`

---

## 4. Add Required Input Files

Place the following files inside the `input/` folder:

- `raw_data.xlsx`
- `company_info.csv`
- `payer_info.csv`
- `bir_form.pdf`
- `coordinates.json`

--- 

## 5. Run the Program

From the project root:

- Mac: `python3 main.py`  
- Windows: `python main.py`

---

## 6. Output

After running:

- `output/cleaned_data.csv` → processed data  
- `output/ewt_forms_QX/` → generated PDFs (one per company)  

`QX` = quarter number (Q1, Q2, etc.)

---



