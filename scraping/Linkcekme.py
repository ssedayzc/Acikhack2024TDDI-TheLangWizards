import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# ChromeDriver'ın yolunu belirtin
chrome_driver_path = r'C:\Users\bugra\Desktop\gogıl\chromedriver.exe'

# Chrome seçenekleri
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

# WebDriver'ı başlat
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Google Scholar sayfasını aç
driver.get('https://scholar.google.com.tr/citations?hl=tr&user=SSFMgB0AAAAJ&view_op=list_works&sortby=pubdate')

# Sayfanın yüklenmesini bekle
time.sleep(3)

# Makale bilgilerini toplamak için boş bir liste oluştur
articles = []

# Makale listesi tablosundaki satırları bul
rows = driver.find_elements(By.CSS_SELECTOR, 'tr.gsc_a_tr')

for row in rows:
    title = row.find_element(By.CSS_SELECTOR, 'a.gsc_a_at').text
    authors = row.find_element(By.CSS_SELECTOR, 'div.gs_gray').text
    publication = row.find_elements(By.CSS_SELECTOR, 'div.gs_gray')[1].text
    year = row.find_element(By.CSS_SELECTOR, 'span.gsc_a_h').text
    citations = row.find_element(By.CSS_SELECTOR, 'a.gsc_a_ac').text
    articles.append({
        'Title': title,
        'Authors': authors,
        'Publication': publication,
        'Year': year,
        'Citations': citations
    })

# WebDriver'ı kapat
driver.quit()

# Verileri bir DataFrame'e dönüştür
df = pd.DataFrame(articles)

# DataFrame'i bir Excel dosyasına kaydet
excel_file_path = r'C:\Users\bugra\Desktop\gogıl\scholar_articles.xlsx'
df.to_excel(excel_file_path, index=False)

print(f"Veriler başarıyla {excel_file_path} dosyasına kaydedildi.")
