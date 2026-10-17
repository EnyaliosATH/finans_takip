#!/usr/bin/env python3
"""
Finans Takip - Döviz Kuru Takip ve Kayıt Sistemi
Hafif, bağımsız ve SQLite destekli canlı döviz kuru takipçisi.
"""

import sys
import os
import json
import sqlite3
import argparse
import time
from datetime import datetime

# Renkler (ANSI Escape Kodları)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    DANGER = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

DB_FILE = "finans.db"
API_URL = "https://open.er-api.com/v6/latest/USD"

def get_connection():
    """SQLite veritabanı bağlantısı oluşturur."""
    conn = sqlite3.connect(DB_FILE)
    return conn

def init_db():
    """Veritabanını ve 'kurlar' tablosunu hazırlar."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kurlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doviz_turu TEXT NOT NULL,
            fiyat REAL NOT NULL,
            tarih TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def fetch_exchange_rates():
    """
    Canlı döviz kurlarını çeker.
    Önce 'requests' kütüphanesini dener; yüklü değilse standart 'urllib' kütüphanesine geçer.
    """
    try:
        import requests
        response = requests.get(API_URL, timeout=10)
        data = response.json()
    except ImportError:
        import urllib.request
        import ssl
        try:
            ctx = ssl.create_default_context()
        except Exception:
            ctx = ssl._create_unverified_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(
            API_URL,
            headers={'User-Agent': 'FinansTakip/2.0 (CLI Currency Tracker)'}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))

    if data.get("result") != "success":
        raise ValueError("Döviz sağlayıcı servisinden geçerli yanıt alınamadı.")

    rates = data.get("rates", {})
    try_rate = rates.get("TRY")
    if not try_rate:
        raise ValueError("TRY kuru bulunamadı.")

    usd_try = round(try_rate, 2)
    eur_try = round(try_rate / rates.get("EUR", 1), 2)
    gbp_try = round(try_rate / rates.get("GBP", 1), 2)
    chf_try = round(try_rate / rates.get("CHF", 1), 2)

    return {
        "USD": usd_try,
        "EUR": eur_try,
        "GBP": gbp_try,
        "CHF": chf_try
    }

def get_latest_stored_rate(currency):
    """Belirtilen döviz türünün veritabanındaki son kayıtlı fiyatını döndürür."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT fiyat, tarih FROM kurlar WHERE doviz_turu = ? ORDER BY id DESC LIMIT 1",
        (currency,)
    )
    result = cursor.fetchone()
    conn.close()
    return result

def save_rates(rates_dict, timestamp):
    """Döviz kurlarını veritabanına kaydeder."""
    conn = get_connection()
    cursor = conn.cursor()
    for currency, price in rates_dict.items():
        cursor.execute(
            "INSERT INTO kurlar (doviz_turu, fiyat, tarih) VALUES (?, ?, ?)",
            (currency, price, timestamp)
        )
    conn.commit()
    conn.close()

def format_change(current, previous):
    """Önceki değere göre değişim yüzdesini ve ok işaretini biçimlendirir."""
    if previous is None or previous == 0:
        return f"{Colors.CYAN}  Yeni Kayıt{Colors.RESET}"
    
    diff = current - previous
    percent = (diff / previous) * 100

    if diff > 0:
        return f"{Colors.GREEN}+{percent:.2f}% ▲{Colors.RESET}"
    elif diff < 0:
        return f"{Colors.DANGER}{percent:.2f}% ▼{Colors.RESET}"
    else:
        return f"{Colors.RESET} 0.00% ─{Colors.RESET}"

def print_rates_table(rates_dict, previous_rates, timestamp):
    """Güncel kurları şık bir terminal tablosu olarak yazdırır."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}╔═════════════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}║                    CANLI DÖVİZ KURLARI (TRY)                        ║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}╚═════════════════════════════════════════════════════════════════════╝{Colors.RESET}")
    print(f"{Colors.BOLD}Tarih/Saat:{Colors.RESET} {timestamp}\n")

    print(f"{Colors.BOLD}┌────────┬────────────────┬───────────────────┬───────────────────────┐{Colors.RESET}")
    print(f"{Colors.BOLD}│ Döviz  │   Fiyat (TL)   │    Son Değişim    │   Önceki Kayıt        │{Colors.RESET}")
    print(f"{Colors.BOLD}├────────┼────────────────┼───────────────────┼───────────────────────┤{Colors.RESET}")

    for currency, price in rates_dict.items():
        prev_data = previous_rates.get(currency)
        prev_price = prev_data[0] if prev_data else None
        change_str = format_change(price, prev_price)

        prev_info = f"{prev_price:.2f} TL" if prev_price else "Mevcut Değil"
        print(f"│  {Colors.BOLD}{currency:<4}{Colors.RESET}  │   {price:>7.2f} TL   │   {change_str:<26} │   {prev_info:<18}  │")

    print(f"{Colors.BOLD}└────────┴────────────────┴───────────────────┴───────────────────────┘{Colors.RESET}\n")

def show_history(limit=15):
    """Veritabanındaki geçmiş kayıtları listeler."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, doviz_turu, fiyat, tarih 
        FROM kurlar 
        ORDER BY id DESC 
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"{Colors.WARNING}Veritabanında henüz kayıt bulunmuyor.{Colors.RESET}")
        return

    print(f"\n{Colors.BOLD}{Colors.HEADER}=== SON {len(rows)} KAYIT GEÇMİŞİ ==={Colors.RESET}")
    print(f"{Colors.BOLD}┌──────┬────────┬──────────────┬─────────────────────┐{Colors.RESET}")
    print(f"{Colors.BOLD}│  ID  │ Döviz  │  Fiyat (TL)  │ Tarih               │{Colors.RESET}")
    print(f"{Colors.BOLD}├──────┼────────┼──────────────┼─────────────────────┤{Colors.RESET}")
    for row in rows:
        print(f"│ {row[0]:>4} │  {row[1]:<4}  │   {row[2]:>7.2f} TL │ {row[3]:<19} │")
    print(f"{Colors.BOLD}└──────┴────────┴──────────────┴─────────────────────┘{Colors.RESET}\n")

def show_statistics():
    """Her döviz türü için min, max, ortalama ve toplam kayıt istatistiklerini hesaplar."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT doviz_turu, 
               COUNT(*), 
               MIN(fiyat), 
               MAX(fiyat), 
               AVG(fiyat)
        FROM kurlar 
        GROUP BY doviz_turu
    """)
    stats = cursor.fetchall()
    conn.close()

    if not stats:
        print(f"{Colors.WARNING}İstatistik oluşturmak için yeterli veri yok.{Colors.RESET}")
        return

    print(f"\n{Colors.BOLD}{Colors.HEADER}=== DÖVİZ İSTATİSTİKLERİ (ÖZET) ==={Colors.RESET}")
    print(f"{Colors.BOLD}┌────────┬─────────────┬──────────────┬──────────────┬──────────────┐{Colors.RESET}")
    print(f"{Colors.BOLD}│ Döviz  │ Toplam Kayıt│ En Düşük     │ En Yüksek    │ Ortalama     │{Colors.RESET}")
    print(f"{Colors.BOLD}├────────┼─────────────┼──────────────┼──────────────┼──────────────┤{Colors.RESET}")
    for row in stats:
        print(f"│  {row[0]:<4}  │ {row[1]:>11} │  {row[2]:>8.2f} TL │  {row[3]:>8.2f} TL │  {row[4]:>8.2f} TL │")
    print(f"{Colors.BOLD}└────────┴─────────────┴──────────────┴──────────────┴──────────────┘{Colors.RESET}\n")

def export_data(format_type="csv"):
    """Tüm verileri CSV veya JSON formatında dışa aktarır."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, doviz_turu, fiyat, tarih FROM kurlar ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"{Colors.WARNING}Dışa aktarılacak kayıt bulunamadı.{Colors.RESET}")
        return

    filename = f"kurlar_export_{int(time.time())}.{format_type}"
    if format_type == "csv":
        with open(filename, "w", encoding="utf-8") as f:
            f.write("id,doviz_turu,fiyat,tarih\n")
            for r in rows:
                f.write(f"{r[0]},{r[1]},{r[2]},{r[3]}\n")
    else:
        records = [{"id": r[0], "doviz_turu": r[1], "fiyat": r[2], "tarih": r[3]} for r in rows]
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=4, ensure_ascii=False)

    print(f"{Colors.GREEN}✓ Veriler başarıyla kaydedildi:{Colors.RESET} {filename}")

def run_tracker():
    """Kurları çeker, önceki verilerle karşılaştırır, kaydeder ve ekrana basar."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Mevcut en son kurları hafızaya al (karşılaştırma için)
    currencies = ["USD", "EUR", "GBP", "CHF"]
    previous_rates = {c: get_latest_stored_rate(c) for c in currencies}

    print(f"{Colors.CYAN}⏳ Canlı veriler çekiliyor...{Colors.RESET}")
    rates = fetch_exchange_rates()

    # Veritabanına kaydet
    save_rates(rates, timestamp)

    # Ekrana yazdır
    print_rates_table(rates, previous_rates, timestamp)

def main():
    parser = argparse.ArgumentParser(description="Finans Takip - Döviz Kuru Takip ve Kayıt Sistemi")
    parser.add_argument("--history", type=int, nargs="?", const=15, help="Son N kaydı listeler (Varsayılan: 15)")
    parser.add_argument("--stats", action="store_true", help="Döviz istatistiklerini gösterir (Min, Max, Ortalama)")
    parser.add_argument("--export", choices=["csv", "json"], help="Verileri CSV veya JSON dosyasına aktarır")
    parser.add_argument("--watch", type=int, nargs="?", const=60, help="Belirtilen saniye aralığında canlı takip yapar (Varsayılan: 60)")

    args = parser.parse_args()

    init_db()

    if args.history:
        show_history(args.history)
    elif args.stats:
        show_statistics()
    elif args.export:
        export_data(args.export)
    elif args.watch:
        interval = max(5, args.watch)
        print(f"{Colors.BOLD}{Colors.GREEN}Canlı İzleme Başlatıldı (Her {interval} saniyede bir güncellenir). Çıkmak için Ctrl+C tuşlayın.{Colors.RESET}")
        try:
            while True:
                run_tracker()
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}İzleme durduruldu.{Colors.RESET}")
    else:
        run_tracker()
        show_history(6)

if __name__ == "__main__":
    main()