from scripts import read_data
from scripts import generate_pdf

def main():
    read_data.run()
    generate_pdf.run()

if __name__ == "__main__":
    main()