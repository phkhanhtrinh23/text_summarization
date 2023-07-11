# Text Summarization

## About The Project

This is an implementation of Text Summarization.

## Installation

1. Clone the repo

   ```sh
   git clone https://github.com/phkhanhtrinh23/text_summarization.git
   ```

2. Use any code editor to open the folder **text_summarization**.

## Run
1. Create conda virtual environment: `conda create -n summarizer python=3.9`, activate it: `conda activate summzarizer`
   - In order to run `custom_module`, you should install `tesseract` by command: `sudo apt-get install tesseract-ocr`.

2. You have the following choices:
   - `chatgpt_module`:
      * Install the required packages: `pip install -r requirements.txt`.
      * Start the app: `streamlit run app.py`.
   - `custom_module`:
      * Install the required packages: `pip install -r requirements.txt`.
      * Run the file: `python main.py`
         - `custom` is heuristic summarization.
         - `model` is summarization using LLMs.

## Contribution

Contributions are what make GitHub such an amazing place to be learn, inspire, and create. Any contributions you make are greatly appreciated.

1. Fork the project
2. Create your Contribute branch: `git checkout -b contribute/Contribute`
3. Commit your changes: `git commit -m 'add your messages'`
4. Push to the branch: `git push origin contribute/Contribute`
5. Open a pull request

## Contact

Email: phkhanhtrinh23@gmail.com