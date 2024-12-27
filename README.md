## Software Company Profiler

Software Company Profiler is a comprehensive solution for extracting and organizing detailed information about software companies. It efficiently gathers critical data, including contact details, career opportunities, LinkedIn profiles, office locations, and other key insights, enabling businesses and professionals to streamline research, networking, and decision-making.

## Installation

1. Clone the repository
```bash
git clone git@github.com:PublisherName/Software-Company-Profiler.git
```
2. Change the directory to the project directory
```bash
cd Software-Company-Profiler
```
3. Create a virtual environment using the following command:
```bash
python3 -m venv .venv
```
4. Activate the virtual environment
```bash
source .venv/bin/activate
```
5. Install the required packages using the following command:
```bash
pip install -r requirements.txt
```
6. Cd into the <scraper> directory
```bash
cd <scraper>
```
7. Run the following command to start the web scraper:
```bash
scrapy crawl <scraper> -o <filename> -a url="<url_to_scrape>"
```
8. To manually populate the data, run the following command:
```bash
python main.py <option> --file <file_name>
```
options:
- `--update` : Update the data
- `--view` : Search the data
- `--add` : Add the data


## CSV FORMAT

| name        | address     | city      | website      | career page  | email       | linkedIn    | phone       |
|-------------|-------------|-----------|--------------|--------------|-------------|-------------|-------------|
|             |             |           |              |              |             |             |             |


## Supported Websites

## 1. [NepalYP](https://www.nepalyp.com/)

### Usage:
```bash
cd nepalyp_scraper
```

```bash
scrapy crawl nepalyp -o software.csv -a url="https://www.nepalyp.com/category/Software_applications"
```
