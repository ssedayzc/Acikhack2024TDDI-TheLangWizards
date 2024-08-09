import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# Selenium ve ChromeDriver kurulumları
def create_driver():
    options = Options()
    options.headless = False  # Tarayıcıyı görünür yapmak için
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# CSV dosyasını okuma ve kaldığı yerden devam etmek için başlangıç indexini belirleme
def read_existing_data(filename='turkcell_complaint_contents.csv'):
    try:
        df = pd.read_csv(filename, sep=';')
        return df, len(df)
    except FileNotFoundError:
        return pd.DataFrame(), 0

# Verileri kaydetme fonksiyonu
def save_data(data, filename='turkcell_complaint_contents.csv'):
    try:
        existing_data = pd.read_csv(filename, sep=';')
        df = pd.DataFrame([data])
        df = pd.concat([existing_data, df])
        df.drop_duplicates(inplace=True)
    except FileNotFoundError:
        df = pd.DataFrame([data])
    df.to_csv(filename, index=False, encoding='utf-8-sig', sep=';')

# Şikayet detaylarını kazıyan fonksiyon
def get_complaint_details(driver, detail_url):
    try:
        driver.get(detail_url)
        wait = WebDriverWait(driver, 3)  # Maksimum bekleme süresini 3 saniye olarak ayarladık

        # Şikayet başlığını alma
        title_tag = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.complaint-detail-title'))
        )
        title_text = title_tag.text.strip()

        # Şikayet içeriğini alma
        content_tag = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, 'complaint-detail-description'))
        )
        content = content_tag.text.strip()

        return title_text, content

    except TimeoutException:
        return 'N/A', 'N/A'
    except WebDriverException:
        return 'N/A', 'N/A'
    except Exception:
        return 'N/A', 'N/A'

# Tüm linkler için detayları alma
def scrape_links(start_index):
    df_links = pd.read_csv('C:/Users/bugra/Desktop/türkcellkazıyan/Commentlinks.csv', sep=';')
    links = df_links['Link'].tolist()
    categories = df_links['Category'].tolist()

    driver = create_driver()

    try:
        for index in range(start_index, len(links)):
            link = links[index]
            category = categories[index]
            retries = 3  # Sayfa yüklenmezse veya hata oluşursa yeniden deneme sayısı
            while retries > 0:
                try:
                    start_time = time.time()
                    full_title, content = get_complaint_details(driver, link)
                    elapsed_time = time.time() - start_time

                    data = {
                        'Category': category,
                        'Title': full_title,
                        'Content': content
                    }
                    save_data(data)
                    print(f"Scraped data from link {index + 1}/{len(links)} ({link}) in {elapsed_time} seconds.")
                    time.sleep(0.1)  # Çok fazla istek yapmamak için kısa bir bekleme
                    break  # Başarılı olursa döngüden çık
                except TimeoutException as e:
                    print(f"Timeout error scraping {link}: {e}")
                    retries -= 1
                    time.sleep(1)  # Hata olursa 1 saniye bekle ve tekrar dene
                except WebDriverException as e:
                    print(f"WebDriver error scraping {link}: {e}")
                    retries -= 1
                    time.sleep(1)  # Hata olursa 1 saniye bekle ve tekrar dene
                except Exception as e:
                    print(f"Error scraping {link}: {e}")
                    retries -= 1
                    time.sleep(1)  # Hata olursa 1 saniye bekle ve tekrar dene
            else:
                print(f"Failed to scrape data from link {link} after multiple attempts.")

    finally:
        driver.quit()
        print("Data scraping completed and saved.")

if __name__ == "__main__":
    # Mevcut verileri oku ve kaldığı yerden devam et
    existing_data, start_index = read_existing_data()
    scrape_links(start_index)
