# 📈 Finans Takip - CLI Döviz Kuru Takip & Kayıt Sistemi

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-SQLite3-003B57.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Zero Dependency](https://img.shields.io/badge/Dependencies-Zero%20(Pure%20Stdlib)-brightgreen?style=for-the-badge)](main.py)

Hafif, bağımsız ve terminal tabanlı bir **canlı döviz takipçisi ve kayıt sistemi**. 

Açık kaynaklı döviz kurları API'si üzerinden güncel piyasa verilerini (**USD/TRY**, **EUR/TRY**, **GBP/TRY**, **CHF/TRY**) anlık olarak çeker, önceki kayıtlarla karşılaştırarak değişim oranlarını (yüzde ve yön okuyla) hesaplar ve verileri yerel bir **SQLite** veritabanında arşivler.

---

## 🖥️ Terminal Önizlemesi

```text
╔═════════════════════════════════════════════════════════════════════╗
║                    CANLI DÖVİZ KURLARI (TRY)                        ║
╚═════════════════════════════════════════════════════════════════════╝
Tarih/Saat: 2026-10-18 00:36:36

┌────────┬────────────────┬───────────────────┬───────────────────────┐
│ Döviz  │   Fiyat (TL)   │    Son Değişim    │   Önceki Kayıt        │
├────────┼────────────────┼───────────────────┼───────────────────────┤
│  USD   │     49.52 TL   │   +3.40% ▲        │   47.89 TL            │
│  EUR   │     55.67 TL   │   +0.34% ▲        │   55.48 TL            │
│  GBP   │     65.95 TL   │     Yeni Kayıt    │   Mevcut Değil        │
│  CHF   │     60.07 TL   │     Yeni Kayıt    │   Mevcut Değil        │
└────────┴────────────────┴───────────────────┴───────────────────────┘
```

---

## ✨ Özellikler

- ⚡ **Sıfır Dış Bağımlılık (Zero Dependencies)**: Python'ın standart kütüphaneleri (`urllib`, `ssl`, `sqlite3`, `json`) ile harici hiçbir paket kurmadan anında çalışır. Ortamda `requests` varsa otomatik olarak onu kullanır.
- 🗄️ **Kalıcı SQLite Depolama**: `finans.db` dosyası üzerinde tüm sorgulamaları tarih ve saat damgasıyla saklar.
- 📈 **Anlık Değişim Hesaplama**: Her yeni sorguda veritabanındaki son fiyatla karşılaştırma yapar; artış/azalış yüzdesini hesaplayıp renkli yön okları (▲ / ▼) ile gösterir.
- ⏱️ **Canlı İzleme Modu (Watch Mode)**: Belirlediğiniz saniye aralığında piyasayı terminalden otomatik olarak canlı takip eder.
- 📊 **İstatistik & Özet**: Her döviz birimi için en düşük, en yüksek ve ortalama fiyat analizlerini anında döker.
- 💾 **Dışa Aktarma (Export)**: Veritabanındaki tüm geçmişi tek komutla `.csv` veya `.json` olarak dışarı aktarır.

---

## 🚀 Hızlı Başlangıç

### 1. Depoyu Klonlayın

```bash
git clone https://github.com/EnyaliosATH/finans_takip.git
cd finans_takip
```

### 2. Çalıştırın

Herhangi bir ek kütüphane kurmadan doğrudan çalıştırabilirsiniz:

```bash
python3 main.py
```

*(İsteğe bağlı olarak `pip install -r requirements.txt` komutuyla `requests` kütüphanesini de kurabilirsiniz).*

---

## 📖 Komut Satırı Kullanımı (CLI)

| Komut | Açıklama |
| :--- | :--- |
| `python3 main.py` | Canlı kurları çeker, kaydeder, değişim tablosunu ve son kayıtları gösterir. |
| `python3 main.py --history 25` | Veritabanındaki son 25 kaydı tablo halinde listeler. |
| `python3 main.py --stats` | Her döviz türü için min, max ve ortalama fiyat istatistiklerini hesaplar. |
| `python3 main.py --watch 30` | Her 30 saniyede bir kurları güncelleyerek canlı terminal takibi yapar. |
| `python3 main.py --export csv` | Tüm veritabanı kayıtlarını CSV formatında dışa aktarır. |
| `python3 main.py --export json` | Tüm veritabanı kayıtlarını JSON formatında dışa aktarır. |

---

## 🗄️ Veritabanı Şeması

Veritabanı (`finans.db`), ilk çalıştırmada otomatik olarak oluşturulur:

```sql
CREATE TABLE IF NOT EXISTS kurlar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doviz_turu TEXT NOT NULL,
    fiyat REAL NOT NULL,
    tarih TEXT NOT NULL
);
```

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır. © 2026 [EnyaliosATH](https://github.com/EnyaliosATH).
