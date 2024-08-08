# Acikhack2024TDDI-TheLangWizards

## Temel Özellikler

- **Varlık Çıkartma**: Metinden özel şirket isimlerini ve hizmet isimlerini tanır.
- **Duygu Analizi**: Her varlık için olumlu, olumsuz veya nötr duygu sonuçları sağlar.
  
## Kurulum ve Gereksinimler

### Gereksinimler

### Gereksinimler
- Python 3.7 veya üstü
- FastAPI
- Uvicorn
- Stanza
- Transformers
- PyTorch
- Pydantic
- Logging
- Regular expressions (re)

### Kurulum

1. **Kütüphanelerin Kurulumu:**

   ```bash
   pip install fastapi uvicorn stanza transformers torch pydantic

# Duygu Analizi ve Varlık Çıkarımı API

Bu API, kullanıcıdan gelen metni işleyerek varlıkları (şirket isimleri, hizmetler vb.) ve duygu analizi sonuçlarını döndürür. API, duygu analizi ve varlık çıkarımı için FastAPI tabanlı bir hizmet sağlar. Hugging Face'ten `distilbert-base-uncased-finetuned-sst-2-english` modelini duygu analizi için ve Stanza'dan Türkçe modelini varlık çıkarımı için kullanır.

## İçindekiler

- [Model Detayları](#model-detayları)
- [Proje Kurulumu](#proje-kurulumu)
- [Kullanım](#kullanım)
- [API Uç Noktaları](#api-uç-noktaları)

## Model Detayları

### Duygu Analizi

`distilbert-base-uncased-finetuned-sst-2-english` modeli, Stanford Sentiment Treebank (SST-2) veri kümesinde ince ayar yapılmış, BERT'in damıtılmış bir versiyonudur. Bu model, tam BERT modeline kıyasla daha az parametre ve daha hızlı çıkarım süreleri ile duygu analizi görevlerinde son teknoloji performans sağlar.

Model hakkında daha fazla bilgi için [Hugging Face model sayfasını](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english) ziyaret edin.

### Varlık Çıkarımı

Varlık çıkarımı fonksiyonu, dilbilimsel analiz için doğru ve verimli araçlar koleksiyonu olan Stanza'dan Türkçe modelini kullanır. Stanza kütüphanesi birçok dili destekler ve adlandırılmış varlık tanıma (NER) gibi çeşitli NLP görevleri için sağlam modeller sağlar.

Stanza kütüphanesi hakkında daha fazla bilgi için [Stanza GitHub deposunu](https://github.com/stanfordnlp/stanza) ziyaret edin.

## Proje Kurulumu

### Kurulum

1. Depoyu klonlayın:

    ```bash
    git clone https://github.com/your-username/sentiment-entity-extraction-api.git
    cd sentiment-entity-extraction-api
    ```

2. Gerekli paketleri yükleyin:

    ```bash
    pip install -r requirements.txt
    ```

3. Stanza Türkçe modelini indirin ve başlatın:

    ```python
    import stanza
    stanza.download('tr')
    ```

4. Eğitilmiş BERT model dosyasının (`finetuned_BERT.pth`) uygun dizinde (`content/drive/My Drive/`) olduğundan emin olun.

## Kullanım

FastAPI uygulamasını çalıştırmak için aşağıdaki komutu yürütün:

```bash
uvicorn main:app --reload

Bu, sunucuyu http://127.0.0.1:7000 adresinde başlatacaktır.

API Uç Noktaları
POST /predict/
Giriş metninin duygu analizini yapar ve varlıkları tanımlar.

İstek Gövdesi
text (string): Analiz edilecek metin.

Örnek:
{
  "text": "Fiber 100mb SuperOnline kullanıcısıyım yaklaşık 2 haftadır @Twitch @Kick_Turkey gibi canlı yayın platformlarında 360p yayın izlerken donmalar yaşıyoruz. Başka hiç bir operatörler bu sorunu yaşamazken ben parasını verip alamadığım hizmeti neden ödeyeyim ? @Turkcell"
}

Yanıt:
entity_list (list): Tanımlanan varlıkların listesi.
results (list): Her varlık için duygu analizi sonuçları listesi.
{
  "entity_list": ["Turkcell", "Twitch", "Kick_Turkey"],
  "results": [
    {
      "entity": "Turkcell",
      "sentiment": "negative"
    },
    {
      "entity": "Twitch",
      "sentiment": "neutral"
    },
    {
      "entity": "Kick_Turkey",
      "sentiment": "neutral"
    }
  ]
}



