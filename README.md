# Acikhack2024TDDI-TheLangWizards
# Duygu Analizi API

Bu API, kullanıcıdan gelen metni işleyerek varlıkları (şirket isimleri, hizmetler vb.) ve duygu analizi sonuçlarını döndürür. API, FastAPI kullanılarak geliştirilmiştir ve BERT tabanlı bir sınıflandırıcı ile duygu analizini gerçekleştirir.

## Temel Özellikler

- **Varlık Çıkartma**: Metinden özel şirket isimlerini ve hizmet isimlerini tanır.
- **Duygu Analizi**: Her varlık için olumlu, olumsuz veya nötr duygu sonuçları sağlar.
## Kurulum ve Gereksinimler

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
