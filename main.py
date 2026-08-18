import sqlite3
from datetime import datetime
import requests

# 1. İnternetten Canlı Veri Çekme
url = "https://open.er-api.com/v6/latest/USD"

try:
    response = requests.get(url)
    data = response.json()

    if data["result"] == "success":
        usd_try = round(data["rates"]["TRY"], 2)
        eur_try = round(usd_try / data["rates"]["EUR"], 2)
        su_anki_zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 2. Veritabanı Bağlantısı ve Tablo Oluşturma
        conn = sqlite3.connect("finans.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS kurlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doviz_turu TEXT,
                fiyat REAL,
                tarih TEXT
            )
        """
        )

        # 3. Verileri Tabloya Ekleme (SQL INSERT)
        cursor.execute(
            "INSERT INTO kurlar (doviz_turu, fiyat, tarih) VALUES (?, ?, ?)",
            ("USD", usd_try, su_anki_zaman),
        )
        cursor.execute(
            "INSERT INTO kurlar (doviz_turu, fiyat, tarih) VALUES (?, ?, ?)",
            ("EUR", eur_try, su_anki_zaman),
        )

        # Değişiklikleri kaydet
        conn.commit()

        # 4. Veritabanındaki Verileri Okuma ve Ekrana Basma (SQL SELECT)
        print("--- VERITABANINA KAYDEDILEN KAYITLAR ---")
        cursor.execute("SELECT * FROM kurlar")
        tum_kayitlar = cursor.fetchall()

        for kayit in tum_kayitlar:
            print(f"ID: {kayit[0]} | Doviz: {kayit[1]} | Fiyat: {kayit[2]} TL | Tarih: {kayit[3]}")

        conn.close()

    else:
        print("Veri cekilemedi!")

except Exception as e:
    print("Hata cikti:", e)