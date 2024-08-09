import uvicorn
import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import stanza
from transformers import pipeline
import logging
import re

# stanza modelini yükleme ve başlatma
stanza.download('tr')
nlp = stanza.Pipeline('tr')

# Duygu analizi için transformers pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

# Proje dosya yolunu sisteme ekliyoruz
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# FastAPI uygulaması başlatılıyor
app = FastAPI()

# API'ye gelen isteklerde kullanılacak veri modeli
class Item(BaseModel):
    text: str = Field(..., example="""Fiber 100mb SuperOnline kullanıcısıyım yaklaşık 2 haftadır @Twitch @Kick_Turkey gibi canlı yayın platformlarında 360p yayın izlerken donmalar yaşıyoruz. Başka hiç bir operatörler bu sorunu yaşamazken ben parasını verip alamadığım hizmeti neden ödeyeyim ? @Turkcell """)

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
TURKISH_COMPANIES_SERVICES = [
    "Turkcell", "Türk Telekom", "Vodafone", "Superonline", "TTNET", "BİM", "A101", 
    "Migros", "Hepsiburada", "Trendyol", "N11", "Getir", "Yemeksepeti", "PTT",
    "Akbank", "Garanti Bankası", "İş Bankası", "Yapı Kredi", "Halkbank", "Ziraat Bankası",
    "Enpara", "QNB Finansbank", "Denizbank", "ING Bank", "Şok", "CarrefourSA",
    "MediaMarkt", "Teknosa", "Vatan Bilgisayar", "Koçtaş", "IKEA", "Decathlon",
    "LC Waikiki", "Defacto", "Koton", "Mavi", "Colin's", "Adidas", "Nike",
    "Penti", "Boyner", "Morhipo", "Markafoni", "GittiGidiyor", "Amazon Türkiye",
    "Opet", "Shell", "BP", "Total", "Aytemiz", "Petrol Ofisi", "Tüpraş",
    "THY", "Pegasus", "AnadoluJet", "SunExpress", "AtlasGlobal", "Onur Air",
    "TurkNet", "D-Smart", "Digitürk", "Netflix", "BluTV", "Exxen", "Gain",
    "Spotify", "Apple Music", "YouTube Music", "Fizy", "TV+", "Tivibu",
    "Twitter", "Instagram", "Facebook", "Snapchat", "Twitch", "Kick_Turkey",
    "TikTok", "LinkedIn", "WhatsApp", "Telegram", "Signal", "Discord"
]

def extract_custom_entities(text: str) -> List[str]:
    # '@' işaretinden sonra gelen kelimeleri bulma
    at_mentions = re.findall(r'@(\w+)', text)

    # Türkiye'deki özel şirketler ve hizmet isimlerini bulma
    custom_entities = [company for company in TURKISH_COMPANIES_SERVICES if company.lower() in text.lower()]

    # "hiç bir" ifadesini ve sonrasındaki kelimeyi bulma
    hic_bir_matches = re.findall(r'hiç bir (\w+)', text, re.IGNORECASE)
    hic_bir_entities = ["hiç bir " + match for match in hic_bir_matches]

    return at_mentions + custom_entities + hic_bir_entities

# Sentiment skoru sınıflandırma fonksiyonu
def classify_sentiment(score: float) -> str:
    if score > 0.6:
        return "olumlu"
    elif score < 0.4:
        return "olumsuz"
    else:
        return "nötr"

# /predict/ endpoint'i için POST isteği karşılayan fonksiyon
@app.post("/predict/", response_model=PredictionResponse)
async def predict(item: Item):
    try:
        # Giriş metni
        input_text = item.text

        # 1. Entity Extraction (Entity'lerin Tespit Edilmesi)
        doc = nlp(input_text)
        entities = [ent.text for ent in doc.ents]

        # Özel entity'leri bulma ve ekleme
        custom_entities = extract_custom_entities(input_text)
        entities.extend(custom_entities)
        
        # Duplicate entity'leri kaldırma
        entities = list(set(entities))
        
        # 2. Sentiment Analysis (Duygu Analizi)
        sentiments = []
        for entity in entities:
            # Entity'nin bulunduğu kısmın sentiment analizi
            sentiment_result = sentiment_pipeline(entity)[0]
            sentiment_score = sentiment_result['score']  # Sentiment skoru

            # Skoru sınıflandırma
            sentiment_class = classify_sentiment(sentiment_score)

            sentiments.append({"entity": entity, "sentiment": sentiment_class})

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
    uvicorn.run(app, host="127.0.0.1", port=7000)
