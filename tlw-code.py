import uvicorn
import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import stanza
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import logging
import re

# stanza modelini yükleme ve başlatma
stanza.download('tr')
nlp = stanza.Pipeline('tr')

# Duygu analizi için transformer modelini yükleme
model_path = '/Users/mucahitozturk/Downloads/model_save/'
model = AutoModelForSequenceClassification.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)

# Modeli cihazda çalıştırmaya hazırlama (GPU veya CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Proje dosya yolunu sisteme ekliyoruz
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# FastAPI uygulaması başlatılıyor
app = FastAPI()

# Türkiye'deki özel şirketler ve hizmet isimlerinin listesini dosyadan okuma
def load_turkish_companies_services(filepath: str) -> List[str]:
    with open(filepath, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file]

# API'ye gelen isteklerde kullanılacak veri modeli
class Item(BaseModel):
    text: str = Field(..., example="""Fiber 100mb SuperOnline kullanıcısıyım yaklaşık 2 haftadır @Twitch @Kick_Turkey gibi canlı yayın platformlarında 360p yayın izlerken donmalar yaşıyoruz. Başka hiç bir operatörler bu sorunu yaşamazken ben parasını verip alamadığım hizmeti neden ödeyeyim? @Turkcell """)

# Örnek çıktının veri modeli
class SentimentResult(BaseModel):
    entity: str
    sentiment: str  # Sentiment sonucu (olumlu, olumsuz veya nötr)

class PredictionResponse(BaseModel):
    entity_list: List[str]
    results: List[SentimentResult]

# Loglama yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Türkiye'deki özel şirketler ve hizmet isimlerinin listesi
TURKISH_COMPANIES_SERVICES = load_turkish_companies_services('turkish_companies_services.txt')

def extract_custom_entities(text: str) -> List[str]:
    # '@' işaretinden sonra gelen kelimeleri bulma
    at_mentions = re.findall(r'@(\w+)', text)
    # Türkiye'deki özel şirketler ve hizmet isimlerini bulma
    custom_entities = []
    for company in TURKISH_COMPANIES_SERVICES:
        pattern = re.compile(rf'\b{company}\w*\b', re.IGNORECASE)  # Şirket adlarını olası eklerle arama
        matches = pattern.findall(text)
        custom_entities.extend(matches)

    # "hiç bir" ifadesini ve sonrasındaki kelimeyi bulma
    hic_bir_matches = re.findall(r'hiç bir (\w+)', text, re.IGNORECASE)
    hic_bir_entities = ["hiç bir " + match for match in hic_bir_matches]

    return at_mentions + custom_entities + hic_bir_entities

def remove_sub_entities(entities: List[str]) -> List[str]:
    # Entity listesinde başka bir entity geçen durumlarda sadece en uzun olanı bırakma
    entities.sort(key=len, reverse=True)  # Entity'leri uzunluklarına göre sırala
    filtered_entities = []
    for entity in entities:
        if not any(entity != longer_entity and entity in longer_entity for longer_entity in filtered_entities):
            filtered_entities.append(entity)
    return filtered_entities

# Entity'lerden ekleri ve baştaki @ işaretini temizleme
def clean_entity_suffixes(entities: List[str]) -> List[str]:
    suffixes = ["'in", "'nin", "'un", "'nun", "'ın", "'nın", "'dan", "'tan", "'den", "'ten"]
    cleaned_entities = []
    for entity in entities:
        # Suffix temizleme
        for suffix in suffixes:
            if entity.endswith(suffix):
                entity = entity[:-len(suffix)]
        
        # @ işaretini temizleme
        if entity.startswith("@"):
            entity = entity[1:]
        
        cleaned_entities.append(entity)
    return cleaned_entities

# Metindeki cümleleri bölme fonksiyonu
def split_sentences(text: str) -> List[str]:
    return re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)

# Duygu analizini sınıflandırma fonksiyonu
def classify_sentiment_from_logits(logits) -> str:
    # Logit'leri olasılıklara dönüştürme
    probabilities = torch.softmax(logits, dim=1)
    
    # Tahmin edilen label'i al
    predicted_label = torch.argmax(probabilities, dim=1).item()
    
    # Label mapping
    label_mapping = {0: "olumsuz", 1: "olumlu"}
    predicted_sentiment = label_mapping.get(predicted_label, "nötr")
    
    return predicted_sentiment

# /predict/ endpoint'i için POST isteği karşılayan fonksiyon
@app.post("/predict/", response_model=PredictionResponse)
async def predict(item: Item):
    try:
        # Giriş metni
        input_text = item.text

        # 1. Entity Extraction (Entity'lerin Tespit Edilmesi)
        doc = nlp(input_text)
        entities = [ent.text for ent in doc.ents]

        # Özel entity'leri bulma ve ekleme (Updated function)
        custom_entities = extract_custom_entities(input_text)
        entities.extend(custom_entities)
        
        # Duplicate entity'leri kaldırma ve normalize etme
        entities = list(set(entities))
        
        # Entity'leri temizleme (başka bir entity geçen durumlarda sadece en uzun olanı bırakma)
        entities = remove_sub_entities(entities)
        
        # Entity'lerden ekleri temizleme
        entities = clean_entity_suffixes(entities)
        
        # Metindeki cümleleri bölme
        sentences = split_sentences(input_text)
        
        # 2. Sentiment Analysis (Duygu Analizi)
        sentiments = []
        if not entities:
            entities.append("N/A")  # Eğer hiçbir entity bulunamazsa "N/A" ekle
            sentiments.append({"entity": "N/A", "sentiment": "nötr"})
        else:
            for entity in entities:
                for sentence in sentences:
                    if entity in sentence:
                        # Cümlenin kelime sayısını kontrol etme
                        if len(sentence.split()) < 3:
                            sentiment_class = "nötr"
                        else:
                            # Input'u encode etme
                            inputs = tokenizer.encode_plus(
                                sentence,
                                add_special_tokens=True,
                                max_length=128,
                                padding='max_length',
                                truncation=True,
                                return_tensors='pt'
                            )
                            input_ids = inputs['input_ids'].to(device)
                            attention_mask = inputs['attention_mask'].to(device)

                            # Model ile tahmin yapma
                            model.eval()
                            with torch.no_grad():
                                outputs = model(input_ids, attention_mask=attention_mask)
                            logits = outputs[0]

                            # Skoru sınıflandırma
                            sentiment_class = classify_sentiment_from_logits(logits)

                        sentiments.append({"entity": entity, "sentiment": sentiment_class})
                        break  # Aynı entity için birden fazla cümle olasılığını ortadan kaldırmak için

        # Sonuçları oluşturuyoruz
        result = {
            "entity_list": entities,
            "results": sentiments
        }

        return result
    
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Uygulamanın ana fonksiyonu, yerel sunucuyu çalıştırır
if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
