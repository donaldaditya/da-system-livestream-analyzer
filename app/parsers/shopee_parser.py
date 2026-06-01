import pandas as pd
from datetime import datetime, timedelta
from app.models.stream import StandardStreamRecord, Platform, StreamType

EXCEL_EPOCH = datetime(1899, 12, 30)

def excel_serial_to_datetime(serial: float) -> datetime:
    return EXCEL_EPOCH + timedelta(days=serial)

def parse_idr(value) -> int:
    if pd.isna(value):
        return 0
    s = str(value).replace("Rp", "").replace(".", "").replace(",", "").strip()
    return int(s) if s.isdigit() else 0

def parse_shopee_export(filepath: str, entity_id: str, stream_type: StreamType) -> list[StandardStreamRecord]:
    df = pd.read_excel(filepath, sheet_name="Sheet1", header=0)
    records = []
    for _, row in df.iterrows():
        start_raw = row.get("Start Time", 0)
        start_time = excel_serial_to_datetime(float(start_raw)) if start_raw else None
        duration_raw = float(row.get("Durasi", 0) or 0)
        avg_dur_raw = float(row.get("Durasi Rata-Rata Menonton", 0) or 0)
        record = StandardStreamRecord(
            entity_id=entity_id,
            platform=Platform.shopee,
            stream_type=stream_type,
            stream_title=str(row.get("Nama Livestream", "")),
            start_time=start_time,
            duration_minutes=duration_raw * 24 * 60,
            gmv_confirmed=parse_idr(row.get("Penjualan (Siap Dikirim)", 0)),
            viewers_total=int(row.get("Penonton", 0) or 0),
            viewers_active=int(row.get("Penonton Aktif", 0) or 0),
            orders_confirmed=int(row.get("Pesanan (Siap Dikirim)", 0) or 0),
            items_sold=int(row.get("Produk Terjual (Siap Dikirim)", 0) or 0),
            avg_view_duration_s=avg_dur_raw * 86400,
            add_to_cart=int(row.get("Tambah ke Keranjang", 0) or 0),
            comments=int(row.get("Komentar", 0) or 0),
        )
        records.append(record)
    return records
