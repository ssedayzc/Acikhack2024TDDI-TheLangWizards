import os
import pandas as pd
from bs4 import BeautifulSoup
import concurrent.futures

# HTML dosyalarının bulunduğu klasör
html_folder = 'C:/Users/bugra/Desktop/turkceldograyan/html_pages'
output_csv = 'C:/Users/bugra/Desktop/turkceldograyan/turkcell_complaints.csv'
input_csv = 'C:/Users/bugra/Desktop/turkceldograyan/Commentlinks.csv'

# Şikayet başlıklarını ve içeriklerini çekip CSV dosyasına yazma fonksiyonu
def process_html_file(filepath, categories):
    try:
        filename = os.path.basename(filepath)
        with open(filepath, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

            # Şikayet başlığını çekme
            title_tag = soup.select_one('h1.complaint-detail-title')
            title_text = title_tag.get_text(strip=True) if title_tag else 'N/A'

            # Şikayet içeriğini çekme
            content_tag = soup.select_one('.complaint-detail-description')
            content = content_tag.get_text(strip=True) if content_tag else 'N/A'

            # Dosya numarasını elde etme
            file_number = int(filename.split('_')[1].split('.')[0])
            category = categories[file_number - 1]  # Kategori listesinden dosya numarasına göre kategoriyi al

            return {
                'Filename': filename,
                'Category': category,
                'Title': title_text,
                'Content': content
            }

    except Exception as e:
        print(f"Error processing file {filename}: {e}")
        return None

def extract_complaints_to_csv(html_folder, output_csv, input_csv):
    data = []
    
    # Varolan CSV dosyasını okuma
    if os.path.exists(output_csv):
        existing_data = pd.read_csv(output_csv, sep=';')
        processed_files = set(existing_data['Filename'].tolist())
    else:
        existing_data = pd.DataFrame(columns=['Filename', 'Category', 'Title', 'Content'])
        processed_files = set()

    # Yorum linkleri ve kategorileri okuma
    df_links = pd.read_csv(input_csv, sep=';')
    categories = df_links['Category'].tolist()

    files = [os.path.join(html_folder, f) for f in os.listdir(html_folder) if f.endswith('.html')]
    files.sort(key=lambda x: int(os.path.basename(x).split('_')[1].split('.')[0]))  # Dosya adlarına göre sırala

    print(f"Found {len(files)} HTML files to process.")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_html_file, filepath, categories): filepath for filepath in files if os.path.basename(filepath) not in processed_files}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                data.append(result)
                print(f"Processed file: {result['Filename']}")

                # Her 100 dosyada bir veriyi CSV dosyasına kaydet
                if len(data) >= 100:
                    df = pd.DataFrame(data)
                    df.to_csv(output_csv, mode='a', header=not os.path.exists(output_csv), index=False, encoding='utf-8-sig', sep=';')
                    data = []  # Data listesini temizle

    # Kalan verileri kaydet
    if data:
        df = pd.DataFrame(data)
        df.to_csv(output_csv, mode='a', header=not os.path.exists(output_csv), index=False, encoding='utf-8-sig', sep=';')

    print("Processing completed.")

if __name__ == "__main__":
    extract_complaints_to_csv(html_folder, output_csv, input_csv)
