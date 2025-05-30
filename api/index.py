from flask import Flask, jsonify
from datetime import datetime
import calendar

from hijri_converter import convert
from lunardate import LunarDate

app = Flask(__name__)

# Pasaran Jawa
pasaran_list = ['Legi', 'Pahing', 'Pon', 'Wage', 'Kliwon']
pasaran_start = datetime(1900, 1, 1)

# Kalender China
chinese_days = ["", "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
                "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
                "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"]

chinese_months = ["", "正月", "二月", "三月", "四月", "五月", "六月",
                  "七月", "八月", "九月", "十月", "冬月", "腊月"]

libur_tetap = {
    datetime(2025, 1, 1): "Tahun Baru Masehi",
    datetime(2025, 3, 29): "Hari Suci Nyepi Tahun Baru Saka 1947",
    datetime(2025, 4, 18): "Wafat Yesus Kristus",
    datetime(2025, 4, 20): "Hari Paskah",
    datetime(2025, 5, 1): "Hari Buruh Internasional",
    datetime(2025, 5, 12): "Hari Raya Waisak 2569 BE",
    datetime(2025, 5, 29): "Kenaikan Yesus Kristus",
    datetime(2025, 6, 9): "Cuti Bersama Idul Adha 1446 Hijriyah",
}

hari_indonesia = {
    "Monday": "Senin",
    "Tuesday": "Selasa",
    "Wednesday": "Rabu",
    "Thursday": "Kamis",
    "Friday": "Jumat",
    "Saturday": "Sabtu",
    "Sunday": "Minggu"
}

def get_bulan(n):
    bulan_id = [
        "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    return bulan_id[n]

bulan_hijriyah_id = {
    1: "Muharram",
    2: "Safar",
    3: "Rabiul Awal",
    4: "Rabiul Akhir",
    5: "Jumadil Awal",
    6: "Jumadil Akhir",
    7: "Rajab",
    8: "Syaban",
    9: "Ramadan",
    10: "Syawal",
    11: "Zulkaidah",
    12: "Zulhijjah"
}

def get_pasaran(date_obj):
    delta_days = (date_obj - pasaran_start).days
    return pasaran_list[delta_days % 5]

def get_tahun_jawa(masehi_year):
    return 1555 + (masehi_year - 2022)

def is_libur_otomatis(masehi_date, hijri, lunar):
    libur = []
    if masehi_date.month == 1 and masehi_date.day == 1:
        libur.append("Tahun Baru Masehi")
    if hijri and hijri.day == 1 and hijri.month == 1:
        libur.append("Tahun Baru Islam")
    if hijri and hijri.month == 10 and hijri.day in [1, 2]:
        libur.append("Hari Raya Idul Fitri")
    if hijri and hijri.month == 12 and hijri.day == 10:
        libur.append("Hari Raya Idul Adha")
    if hijri and hijri.month == 7 and hijri.day == 27:
        libur.append("Isra Mikraj")
    if lunar and lunar.month == 1 and lunar.day == 1:
        libur.append("Tahun Baru Imlek")
    return libur

def get_libur_lengkap(masehi_date, hijri, lunar):
    libur = []
    if masehi_date in libur_tetap:
        libur.append(libur_tetap[masehi_date])
    libur += is_libur_otomatis(masehi_date, hijri, lunar)
    return ", ".join(libur) if libur else None

def generate_bulan(year, month):
    if year < 1 or year > 9999:
        raise ValueError("Tahun harus antara 1 dan 9999")

    month_data = []
    total_days = calendar.monthrange(year, month)[1]

    for day in range(1, total_days + 1):
        masehi_date = datetime(year, month, day)

        # Aman dari error
        try:
            hijri = convert.Gregorian(year, month, day).to_hijri()
        except:
            hijri = None

        try:
            lunar = LunarDate.fromSolarDate(year, month, day)
        except:
            lunar = None

        libur = get_libur_lengkap(masehi_date, hijri, lunar)

        data = {
            "masehi": {
                "tanggal": day,
                "hari": hari_indonesia[masehi_date.strftime('%A')],
                "bulan": get_bulan(month),
                "tahun": year
            },
            "hijriyah": {
                "tanggal": hijri.day if hijri else None,
                "bulan": bulan_hijriyah_id[hijri.month] if hijri else None,
                "tahun": hijri.year if hijri else None
            },
            "jawa": {
                "tanggal": day,
                "pasaran": get_pasaran(masehi_date),
                "bulan": get_bulan(month),
                "tahun": get_tahun_jawa(year)
            },
            "china": {
                "tanggal": chinese_days[lunar.day] if lunar else None,
                "bulan": chinese_months[lunar.month] if lunar else None,
                "tahun": lunar.year if lunar else None
            },
            "libur": libur
        }

        month_data.append(data)
    return month_data

@app.route("/kalender/<int:year>/<int:month>", methods=["GET"])
def get_kalender(year, month):
    try:
        if 1 <= month <= 12:
            data = generate_bulan(year, month)
            return jsonify({"kalender": data})
        else:
            return jsonify({"error": "Bulan harus antara 1-12"}), 400
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return "API Kalender Nasional, Islam, China, Jawa — Support semua tahun!"
