import os
import requests
from bs4 import BeautifulSoup
from debate_dict import debate_dict

class DebateParser:
    def __init__(self):
        self.CONTENT_SELECTOR = "#content-sm"
        self.BASE_DIR = "all_debates_raw"
        self.LOG_FILE = "scrape_log.txt"

    def extract_content_from_url(self, url, selector):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        selected_content = soup.select_one(selector)
        return selected_content.get_text() if selected_content else None

    def write_content_to_file(self, directory, filename, content, mode='w'):
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, filename), mode, encoding='utf8') as file:
            file.write(content)

    def log_message(self, message):
        with open(self.LOG_FILE, 'a', encoding='utf8') as log_file:
            log_file.write(message + "\n")

    def scrape_all_content_and_save(self, debate_dict):
        for year, data in debate_dict.items():
            raw_directory = os.path.join(self.BASE_DIR, year, "raw")

            # Scrape the info page
            info_url = data["info"]
            info_content = self.extract_content_from_url(info_url, self.CONTENT_SELECTOR)
            if info_content:
                self.log_message(f"Successfully scraped {info_url}")
                self.write_content_to_file(raw_directory, "raw-info.txt", info_content)
                self.log_message(f"Saved info content as {os.path.join(raw_directory, 'raw-info.txt')}")
            else:
                self.log_message(f"Error scraping {info_url}")
                continue  # Skip to the next year if scraping fails

            # Scrape the debate transcripts
            for i, (date, transcript_url) in enumerate(data["transcripts"], start=1):
                if transcript_url != "Transcript not available.":
                    transcript_content = self.extract_content_from_url(transcript_url, self.CONTENT_SELECTOR)
                    if transcript_content:
                        self.log_message(f"Successfully scraped {transcript_url}")
                        
                        filename = f"{year}-{date}-debate-raw.txt"
                        file_path = os.path.join(raw_directory, filename)
                        if os.path.isfile(file_path):
                            # If the file exists, append the content
                            self.write_content_to_file(raw_directory, filename, transcript_content, mode='a')
                        else:
                            # If the file does not exist, create it
                            self.write_content_to_file(raw_directory, filename, transcript_content)
                        
                        self.log_message(f"Saved transcript content as {os.path.join(raw_directory, f'{year}-{date}-debate-raw.txt')}")
                    else:
                        self.log_message(f"Error scraping {transcript_url}")

# To run
if __name__ == "__main__":
    parser = DebateParser()
    parser.scrape_all_content_and_save(debate_dict)