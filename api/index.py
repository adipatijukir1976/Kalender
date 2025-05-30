from flask import Flask, render_template
from datetime import datetime
from hijri_converter import Gregorian
from lunardate import LunarDate

app = Flask(__name__, static_folder="../static", template_folder="../templates")

pasaran_list = ["Legi", "Pahing", "Pon", "Wage", "Kliwon"]
bulan_jawa_list = [
    "Sura", "Sapar", "Rabiulawal", "Rabiulakhir", "Jumadilawal", "Jumadilakhir",
    "Rejeb", "Sya'ban", "Ramadhan", "Syawal", "Zulkaidah", "Zulhijjah"
]
hari_zh_dict = {
    "Monday": "星期一", "Tuesday": "星期二", "Wednesday": "星期三",
    "Thursday": "星期四", "Friday": "星期五", "Saturday": "星期六", "Sunday": "星期日"
}

def get_javanese_calendar(today):
    base_date = datetime(1633, 7, 8)
    delta_days = (today - base_date).days
    pasaran = pasaran_list[delta_days % 5]
    javanese_day = (delta_days % 30) + 1
    javanese_month = bulan_jawa_list[(delta_days // 30) % 12]
    javanese_year = 1555 + (delta_days // 354)
    return {
        "tgl": javanese_day,
        "bulan": f"{javanese_month} {javanese_year}",
        "pasaran": pasaran
    }

@app.route('/')
def index():
    today = datetime.now()
    hari = today.strftime("%A")
    gregorian = {
        "bulan": today.strftime("%B").upper(),
        "bulan_zh": f"{today.month}月",
        "tahun": today.year,
        "tanggal": today.day,
        "minggu_ke": f"MINGGU KE {today.isocalendar()[1]}",
        "hari": hari.upper(),
        "hari_en": hari,
        "hari_zh": hari_zh_dict.get(hari, "")
    }

    hijri = Gregorian(today.year, today.month, today.day).to_hijri()
    lunar = LunarDate.fromSolarDate(today.year, today.month, today.day)
    imlek = {
        "tgl": lunar.day,
        "bulan": lunar.month,
        "tahun": lunar.year + 2637,
        "catatan": "Tahun Baru Imlek" if lunar.day == 1 and lunar.month == 1 else ""
    }

    jawa = get_javanese_calendar(today)

    return render_template("index.html", gregorian=gregorian, hijri=hijri, imlek=imlek, jawa=jawa)
  
