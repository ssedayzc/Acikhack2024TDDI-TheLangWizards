import time
import pandas as pd
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# Global değişkenler
last_index = 0

# User-Agent listesi
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3', 
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0.3 Safari/602.3.12',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36 OPR/62.0.3331.116',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
]

# Selenium ve ChromeDriver kurulumları
def create_driver():
    options = Options()
    options.headless = False
    options.add_argument(f'user-agent={random.choice(user_agents)}')
    options.add_argument("--start-maximized")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-webgl")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# HTML dosyasını kaydetme fonksiyonu
def save_html(content, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

# Başlangıç indexini belirleme
def get_start_index(output_folder):
    files = os.listdir(output_folder)
    if not files:
        return 0
    files = [f for f in files if f.endswith('.html')]
    files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    last_file = files[-1]
    last_index = int(last_file.split('_')[1].split('.')[0])
    return last_index

# Tüm linkler için detayları alma ve HTML olarak kaydetme
def scrape_links(input_csv, output_folder):
    global last_index

    df_links = pd.read_csv(input_csv, sep=';')
    links = df_links['Link'].tolist()
    categories = df_links['Category'].tolist()

    start_index = get_start_index(output_folder)
    driver = create_driver()

    retry_count = 0

    try:
        for index in range(start_index, len(links)):
            link = links[index]
            category = categories[index]
            retries = 3
            while retries > 0:
                try:
                    start_time = time.time()
                    driver.get(link)
                    wait = WebDriverWait(driver, 10)  # Maksimum bekleme süresini 10 saniye olarak ayarladık
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.complaint-detail-title')))
                    
                    html_content = driver.page_source
                    file_name = f'{output_folder}/page_{index + 1}.html'
                    save_html(html_content, file_name)
                    
                    print(f"Saved HTML for link {index + 1}/{len(links)} ({link}).")
                    last_index = index
                    time.sleep(random.uniform(1, 5))
                    
                    break
                except TimeoutException as e:
                    print(f"Timeout error scraping {link}: {e}")
                    retries -= 1
                    time.sleep(1)
                except WebDriverException as e:
                    print(f"WebDriver error scraping {link}: {e}")
                    retries -= 1
                    time.sleep(1)
                except Exception as e:
                    print(f"Error scraping {link}: {e}")
                    retries -= 1
                    time.sleep(1)
            else:
                print(f"Failed to scrape data from link {link} after multiple attempts.")
                driver.quit()
                driver = create_driver()
                retry_count = 0
    finally:
        driver.quit()
        print("HTML pages saved.")

if __name__ == "__main__":
    input_csv = 'C:/Users/bugra/Desktop/turkceldograyan/Commentlinks.csv'
    output_folder = 'C:/Users/bugra/Desktop/turkceldograyan/html_pages'
    
    os.makedirs(output_folder, exist_ok=True)
    
    scrape_links(input_csv, output_folder)
