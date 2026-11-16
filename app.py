#*********************Login.py********************
import socket
import os
import getpass
import requests
import matplotlib.pyplot as plt # برای رسم نمودار
from datetime import datetime  #برای تبدیل زمان‌های عددی به ساعت و دقیقه
import time
import yfinance

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
HISTORY_URL = "https://archive-api.open-meteo.com/v1/archive"
PRICE_URL = "https://api.coingecko.com/api/v3/simple/price"


# تبدیل کد استاندارد WMO به متن
#The API only returns numeric weather codes. To display descriptions, map the codes on the client.
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

def has_internet():
    """بررسی می‌کند اینترنت وصل است یا نه (True یا False برمی‌گرداند)."""
    # در ابتدا فرض می‌کنیم اینترنت وصل نیست
    result = False

    # چند سرور معروف (آدرس و پورت) را امتحان می‌کنیم؛ کافی است به یکی وصل شویم
    #لیست سرور ها و هر سرور یه تاپل دو عضوی است
    servers = [
        ("8.8.8.8", 53),
        ("1.1.1.1", 443),
        ("1.1.1.1", 53),
        ("9.9.9.9", 53),
        ("8.8.8.8", 443),
    ]

    for server in servers:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        code = sock.connect_ex(server)
        sock.close()
        # عدد 0 یعنی اتصال موفق بوده؛ دیگر لازم نیست بقیه را امتحان کنیم
        if code == 0:
            result = True
            break

    return result

def Calc(num1, num2):
    sum = num1 + num2
    mul = num1 * num2
    sub = num1 - num2
    if num2 == 0:
        div ="Error div by zero"
    else:
        div = num1 / num2
    return sum,mul,sub , div

def BMI(Weight,Height):
    if Height > 0:
        Height = Height / 100
        bmi = Weight / (Height * Height)
        if bmi < 18.5:
            res="\033[1;34mYou are: Underweight\033[0m"
        elif 18.5 <= bmi < 25:
            res="\033[1;32mYou are: Normal\033[0m"      
        elif 25 <= bmi < 30:
            res="\033[1;33mYou are: Overweight\033[0m"    
        else:
            res="\033[1;31mYou are: Obese\033[0m"       
    else:
        bmi="Error! divide by zero"
        res=None

    return bmi, res


def Fibonachi(fibo):
    n1 = 1
    n2 = 1
    if fibo <= 0:
        return"\033[1;31mYour number must be more than zero!\033[0m"
    if fibo == 1: 
        return[n1]
    if fibo == 2:
        return[n1,n2]
    if fibo >= 3:
        i=3   
        res=[n1,n2]
        while fibo >=i:
            n3= n1+n2
            res.append(n3)
#  شیفت دادن اعداد برای دور بعدی:
            n1=n2
            n2=n3
            i=i+1
        return res

def CreditCard(credit):
    bank_names = {
    "603799": "Melli",
    "603769": "Saderat",
    "603770": "Keshavarzi",
    "610433": "Mellat",
    "991975": "Mellat",
    "589210": "Sepah",
    "627353": "Tejarat",
    "585983": "Tejarat",
    "628023": "Maskan",
    "589463": "Refah",
    "502229": "Pasargad",
    "639347": "Pasargad",
    "504172": "Resalat",
    "622106": "Parsian",
    "621986": "Saman",
    "636214": "Ayandeh"}
    if len(credit) == 16 :
        newCredit = credit[0:4]+"*"*8+credit[12:16]    # تکرار ستاره
        preNumber = credit[0:6]
        bank =bank_names.get(preNumber)
    else:
        newCredit="\033[1;31mYour Creditcard number is wrong! You must enter 16 digits \033[0m"
        bank= "unknown " 
    return newCredit,bank


def PasswordCheacker(password):
    score = 0
    result=""
    emtiaz =[]
    if len(password) >= 8:
        score +=1
        emtiaz.append(1)
    if not password.isdigit():
        score +=1
        emtiaz.append(2)

    if not password.isalpha():
        score +=1
        emtiaz.append(3)

    if password != password.lower():
        score +=1
        emtiaz.append(4)
    if password != password.upper():
        score +=1
        emtiaz.append(5)
    match score:
        case 0| 1 | 2:
            result ="\033[1;33mWeak Password \033[0m "
        case 3 | 4:
            result ="\033[1;34mMedium Password \033[0m"
        case 5:
            result ="\033[1;32mStrong Password \033[0m"

    return score , result , emtiaz

#-----------------------------------------------------Wheather
def degrees_to_direction(degrees):
    """زاویه‌ی باد (۰ تا ۳۶۰) را به جهت جغرافیایی تبدیل می‌کند."""
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round(degrees / 45) % 8
    return directions[index]

def air_quality_text(aqi):
    """شاخص کیفیت هوای اروپایی (European AQI) را به متن تبدیل می‌کند."""
    if aqi is None:
        return "Unknown"
    elif aqi < 20:
        return "Good"
    elif aqi < 40:
        return "Fair"
    elif aqi < 60:
        return "Moderate"
    elif aqi < 80:
        return "Poor"
    elif aqi < 100:
        return "Very poor"
    else:
        return "Extremely poor"

    def find_city(city):
        """اطلاعات شهر (مختصات، جمعیت، ارتفاع و ...) را برمی‌گرداند."""
        params = {"name": city, "count": 1}
        response = requests.get(GEO_URL, params=params, timeout=10)
        data = response.json()

        if "results" not in data:
            return None

        return data["results"][0]

def get_weather(place, temp_unit, wind_unit, days):
    """وضعیت فعلی، پیش‌بینی ساعتی امروز و پیش‌بینی روزانه را می‌گیرد."""
    params = {
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "current": (
            "temperature_2m,apparent_temperature,relative_humidity_2m,is_day,"
            "precipitation,cloud_cover,pressure_msl,wind_speed_10m,"
            "wind_direction_10m,wind_gusts_10m,weather_code"
        ),
        "hourly": "temperature_2m",
        "daily": (
            "weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,"
            "precipitation_sum,precipitation_probability_max,wind_speed_10m_max"
        ),
        "forecast_days": days,
        "timezone": "auto",
        "temperature_unit": temp_unit,
        "wind_speed_unit": wind_unit,
    }
    response = requests.get(WEATHER_URL, params=params, timeout=10)
    return response.json()


def find_city(city):
    """اطلاعات شهر (مختصات، جمعیت، ارتفاع و ...) را برمی‌گرداند."""
    params = {"name": city, "count": 1}
    response = requests.get(GEO_URL, params=params, timeout=10)
    data = response.json()

    if "results" not in data:
        return None

    return data["results"][0]


def get_air_quality(place):
    """کیفیت هوا را می‌گیرد. اگر موجود نباشد None برمی‌گرداند."""
    params = {
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "current": "european_aqi,pm10,pm2_5",
    }
    response = requests.get(AIR_URL, params=params, timeout=10)
    data = response.json()

    if "current" not in data:
        return None

    return data["current"]


def get_last_year(place, temp_unit):
    """آب‌وهوای همین روز در سال گذشته را از آرشیو می‌گیرد."""
    last_year = date.today() - timedelta(days=365)

    params = {
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "start_date": str(last_year),
        "end_date": str(last_year),
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
        "temperature_unit": temp_unit,
    }
    response = requests.get(HISTORY_URL, params=params, timeout=30)
    data = response.json()

    if "daily" not in data:
        return None

    return {
        "date": str(last_year),
        "min": data["daily"]["temperature_2m_min"][0],
        "max": data["daily"]["temperature_2m_max"][0],
        "rain": data["daily"]["precipitation_sum"][0],
        "temp_unit": data["daily_units"]["temperature_2m_max"],
        "rain_unit": data["daily_units"]["precipitation_sum"],
    }


def show_report(place, weather, air, last_year):
    """گزارش کامل یک شهر را چاپ می‌کند."""
    current = weather["current"]
    units = weather["current_units"]
    hourly = weather["hourly"]
    daily = weather["daily"]
    daily_units = weather["daily_units"]

    print("\n" + "=" * 50)
    print(f"{place['name']}, {place.get('admin1', '')}, {place.get('country', '')}")
    print("=" * 50)

    # اطلاعات خود شهر
    print("\n[City info]")
    print(f"  Population: {place.get('population', 'unknown')}")
    print(f"  Elevation: {place.get('elevation', 'unknown')} m")
    print(f"  Timezone: {place.get('timezone', 'unknown')}")

    # وضعیت فعلی
    if current["is_day"] == 1:
        day_or_night = "Day"
    else:
        day_or_night = "Night"

    condition = WEATHER_CODES.get(current["weather_code"], "Unknown")
    direction = degrees_to_direction(current["wind_direction_10m"])

    print("\n[Current weather]")
    print(f"  Condition: {condition} ({day_or_night})")
    print(f"  Temperature: {current['temperature_2m']} {units['temperature_2m']} "
          f"(feels like {current['apparent_temperature']} {units['apparent_temperature']})")
    print(f"  Humidity: {current['relative_humidity_2m']} {units['relative_humidity_2m']}")
    print(f"  Precipitation: {current['precipitation']} {units['precipitation']}")
    print(f"  Cloud cover: {current['cloud_cover']} {units['cloud_cover']}")
    print(f"  Pressure: {current['pressure_msl']} {units['pressure_msl']}")
    print(f"  Wind: {current['wind_speed_10m']} {units['wind_speed_10m']} from {direction} "
          f"({current['wind_direction_10m']}°)")
    print(f"  Wind gusts: {current['wind_gusts_10m']} {units['wind_gusts_10m']}")

    # دمای امروز هر ۳ ساعت
    print("\n[Today by hour]")
    for hour in range(0, 24, 3):
        time_text = hourly["time"][hour][11:16]
        print(f"  {time_text}  {hourly['temperature_2m'][hour]} {units['temperature_2m']}")

    # پیش‌بینی روزانه
    print("\n[Daily forecast]")
    for i in range(len(daily["time"])):
        day_condition = WEATHER_CODES.get(daily["weather_code"][i], "Unknown")
        print(f"  {daily['time'][i]}: {day_condition}")
        print(f"    Min / Max: {daily['temperature_2m_min'][i]} / "
              f"{daily['temperature_2m_max'][i]} {daily_units['temperature_2m_max']}")
        print(f"    Precipitation: {daily['precipitation_sum'][i]} {daily_units['precipitation_sum']}, "
              f"chance up to {daily['precipitation_probability_max'][i]}"
              f"{daily_units['precipitation_probability_max']}")
        print(f"    Max wind: {daily['wind_speed_10m_max'][i]} {daily_units['wind_speed_10m_max']}")
        print(f"    Sunrise: {daily['sunrise'][i][11:16]}   Sunset: {daily['sunset'][i][11:16]}")

    # کیفیت هوا
    print("\n[Air quality]")
    if air is None:
        print("  Not available for this location.")
    else:
        aqi = air.get("european_aqi")
        print(f"  European AQI: {aqi} ({air_quality_text(aqi)})")
        print(f"  PM2.5: {air.get('pm2_5')} µg/m³   PM10: {air.get('pm10')} µg/m³")

    # همین روز در سال گذشته
    print("\n[Same day last year]")
    if last_year is None:
        print("  Not available for this location.")
    else:
        print(f"  {last_year['date']}: min {last_year['min']} / max {last_year['max']} "
              f"{last_year['temp_unit']}, precipitation {last_year['rain']} {last_year['rain_unit']}")


def process_city(city, temp_unit, wind_unit, days):
    """همه‌ی مراحل مربوط به یک شهر را انجام می‌دهد."""
    place = find_city(city)
    if place is None:
        print(f"\n{city}: City not found!")
        return

    weather = get_weather(place, temp_unit, wind_unit, days)
    if "current" not in weather:
        print(f"\n{city}: Weather data is not available.")
        return

    air = get_air_quality(place)
    last_year = get_last_year(place, temp_unit)
    show_report(place, weather, air, last_year)
#-------------------------------------------------------------Crypto Price                        
def get_crypto_price(coins) :

    # کار تخصصی: گرفتن قیمت ارزها از CoinGecko
    # ورودی: لیست نام ارزها، مثلا ["bitcoin", "ethereum"]
    # خروجی: دیکشنری قیمت‌ها، مثلا {"bitcoin": {"usd": 60000}, ...}
    url = "https://api.coingecko.com/api/v3/simple/price"
    params ={"ids": ",".join(coins), 
              "vs_currencies": "usd"
            } #لیست کوین رو بگیر و با جوین به رشته تبدیل کن # قیمت بر حسب دلار امریکا بده

    response = requests.get(url, params=params, timeout=10)
    return response.json()

#-------------------------------------------------------------------Crypto Figure

def format_time(milliseconds):
    dt = datetime.fromtimestamp(milliseconds / 1000 )
    # تبدیل زمانِ میلی‌ثانیه‌ای به متن قابل خواندن
    return dt.strftime("%Y-%m-%d %H:%M")

def get_candles(symbol, interval, count):
    # کار تخصصی ۱: گرفتن کندل‌های قیمت یک ارز
    # ورودی: نماد ارز (مثل BTC)، فاصله‌ی زمانی هر کندل (1m, 1h, 1d) و تعداد کندل‌ها
    # خروجی: لیستی از کندل‌ها (هر کندل یک دیکشنری)؛ اگر ارز پیدا نشود، لیست خالی
    url = "https://data-api.binance.vision/api/v3/klines"

    params = {
    "symbol": symbol.upper() + "USDT",
    "interval": interval,
    "limit": count
    }
    response = requests.get(url, params=params, timeout=10)
    print("STATUS CODE:", response.status_code)
    print("RESPONSE TEXT:", response.text)

    # اگر نماد ارز اشتباه باشد، کد جواب ۲۰۰ نیست
    if response.status_code != 200:
        return []

    data = response.json()
    print("DEBUG DATA:", data) # این خط را موقتاً اضافه کن


    candles = []
    #item=[1710123456789, "65000.5", "65500.0", "64800.0", "65200.0", ...] # قیمتها بصورت رشته ارسال میشه

    for item in data:
        # item = [زمان، باز شدن، بیشترین، کمترین، بسته شدن، ...]
        candle = {
            "time": item[0],
            "open": float(item[1]), 
            "high": float(item[2]),
            "low": float(item[3]),
            "close": float(item[4]),  

        }
        candles.append(candle)  # یه لیستی از دیکشنری های کندل
    return candles

def draw_chart(candles, title, file_name):
    # کار تخصصی ۲: رسم نمودار کندلی
    fig, ax = plt.subplots(figsize=(12, 6))

    for i in range(len(candles)):
        candle = candles[i]

        # کندل سبز = قیمت بالا رفته، کندل قرمز = قیمت پایین آمده
        #candle["open"]: قیمت باز شدن (اولین قیمت در آن بازه زمانی)
        #candle["close"]: قیمت بسته شدن (آخرین قیمت در آن بازه زمانی)
        if candle["close"] >= candle["open"]:
            color = "green"
        else:
            color = "red"

        # فتیله: خط باریک از کمترین تا بیشترین قیمت
        ax.vlines(i, candle["low"], candle["high"], color=color, linewidth=1)

        # بدنه: مستطیل بین قیمت باز شدن و بسته شدن
        body_height = abs(candle["close"] - candle["open"])  #قدر مطلق  
        body_bottom = min(candle["open"], candle["close"])
        ax.bar(i, body_height, bottom=body_bottom, color=color, width=0.6)

    # روی محور افقی فقط حدود ۸ زمان می‌نویسیم تا شلوغ نشود
    step = max(1, len(candles) // 8)
    positions = []  # شماره ستون‌هایی است که قرار است زیرشان ساعت بخورد (مثلاً ستون ۰، ستون ۸، ستون ۱۶ و…)
    labels = []
    for i in range(0, len(candles), step):
        positions.append(i)
        labels.append(format_time(candles[i]["time"]))  #ساعت و دقیقه candles

    ax.set_xticks(positions)
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_title(title)
    ax.set_xlabel("Time")
    ax.set_ylabel("Price (USD)")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(file_name)
    plt.show()

#-----------------------------------------------------Forex Figure

def get_price_history(coin, seconds):
    # کار تخصصی: گرفتن تاریخچه قیمت یک ارز در بازه‌ی زمانی مشخص
    # ورودی: نام ارز و طول بازه (به ثانیه)
    # خروجی: لیستی از [زمان، قیمت]؛ اگر ارز پیدا نشود، لیست خالی
    now = int(time.time())
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart/range"
    params = {"vs_currency": "usd", "from": now - seconds, "to": now}

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    # اگر نام ارز اشتباه باشد، کلید "prices" در جواب وجود ندارد
    if "prices" in data:
        return data["prices"]
    else:
        return []


# ======================= Colors =======================
RED, GREEN, YELLOW, BLUE, CYAN, RESET = (
    "\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[96m", "\033[0m")
os.system("")  # enables ANSI colors in Windows cmd
    
# ======================= Data =======================
credentials = {"username": "admin", "password": "Py@12345"}

expenses = [
    {"amount": 12.5, "category": "Food", "note": "Lunch"},
    {"amount": 40.0, "category": "Transport", "note": "Taxi"},
    {"amount": 25.0, "category": "Food", "note": "Dinner"},
    {"amount": 80.0, "category": "Shopping", "note": "Shoes"},
    {"amount": 15.0, "category": "Entertainment", "note": "Cinema"},
]

RATES_URL = "https://open.er-api.com/v6/latest/USD"  # no API key needed

# approximate rates used when the internet / API is not available (1 USD = ...)
FALLBACK_RATES = {"EUR": 0.92, "GBP": 0.79, "TRY": 35.0, "JPY": 150.0}


# ======================= Skeleton =======================
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    print(CYAN + r"""
  +-----------------------------------+
  |   $$  EXPENSE  TRACKER  v1.0  $$  |
  +-----------------------------------+
""" + RESET)


def login(max_attempts=3):
    for attempt in range(1, max_attempts + 1):
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        if username == credentials["username"] and password == credentials["password"]:
            print(GREEN + "Login successful!" + RESET)
            return True
        print(RED + f"Wrong username or password ({attempt}/{max_attempts})" + RESET)
    return False


def print_menu():
    print(YELLOW + "=========== MENU ===========" + RESET)
    items = ["Add expense", "Show expenses", "Statistics", "Filter by category",
             "Chart", "Convert total to another currency", "Change password", "Exit"]
    for number, title in enumerate(items, 1):
        print(f"  {BLUE}{number}{RESET}. {title}")


# ======================= Helpers =======================
def read_positive_float(prompt):
    while True:
        text = input(prompt).strip()
        try:
            value = float(text)
            if value > 0:
                return value
            print(RED + "Value must be greater than zero." + RESET)
        except ValueError:
            print(RED + "Please enter a valid number." + RESET)


def check_password_strength(password):
    """Return a list of problems (empty list = strong password)."""
    problems = []
    if len(password) < 8:
        problems.append("at least 8 characters")
    if not any(c.isupper() for c in password):
        problems.append("at least one uppercase letter")
    if not any(c.islower() for c in password):
        problems.append("at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        problems.append("at least one digit")
    if password.isalnum():
        problems.append("at least one special character")
    return problems


# ======================= Options =======================
def add_expense():
    amount = read_positive_float("Amount ($): ")
    category = input("Category: ").strip().title() or "Other"
    note = input("Note: ").strip()
    expenses.append({"amount": amount, "category": category, "note": note})
    print(GREEN + "Expense added." + RESET)


def show_expenses(items=None):
    items = expenses if items is None else items
    if not items:
        print(RED + "No expenses found." + RESET)
        return
    print(f"{'#':<4}{'Amount':>10}  {'Category':<15}Note")
    print("-" * 45)
    for index, e in enumerate(items, 1):
        print(f"{index:<4}{e['amount']:>10.2f}  {e['category']:<15}{e['note']}")


def show_stats():
    if not expenses:
        print(RED + "No expenses yet." + RESET)
        return
    total = sum(e["amount"] for e in expenses)
    biggest = max(expenses, key=lambda e: e["amount"])
    print(f"Count   : {len(expenses)}")
    print(f"Total   : {total:.2f} $")
    print(f"Average : {total / len(expenses):.2f} $")
    print(f"Largest : {biggest['amount']:.2f} $  ({biggest['category']} - {biggest['note']})")


def filter_by_category():
    category = input("Category to search: ").strip().lower()
    result = [e for e in expenses if e["category"].lower() == category]
    show_expenses(result)
    if result:
        print(f"Total of this category: {sum(e['amount'] for e in result):.2f} $")


def show_chart():
    if not expenses:
        print(RED + "Nothing to draw." + RESET)
        return
    totals = {}
    for e in expenses:
        totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]
    plt.figure(figsize=(7, 5))
    plt.bar(list(totals.keys()), list(totals.values()), color="steelblue")
    plt.title("Expenses by category")
    plt.xlabel("Category")
    plt.ylabel("Amount ($)")
    plt.show()


def get_rate(target):
    """Return (rate, is_live). Falls back to FALLBACK_RATES on any error."""
    try:
        response = requests.get(RATES_URL, timeout=10)
        response.raise_for_status()          # HTTP 4xx/5xx (e.g. 429 rate limit) -> HTTPError
        data = response.json()
        if data.get("result") != "success":  # API-level error
            raise ValueError(data.get("error-type", "unknown error"))
        return data["rates"][target], True
    except (requests.RequestException, KeyError, ValueError):
        return FALLBACK_RATES.get(target), False


def convert_total():
    if not expenses:
        print(RED + "No expenses yet." + RESET)
        return
    target = input("Target currency (EUR, GBP, TRY, JPY ...): ").strip().upper()
    rate, live = get_rate(target)
    if rate is None:
        print(RED + "Currency is not supported." + RESET)
        return
    total = sum(e["amount"] for e in expenses)
    print(f"Total: {total:.2f} USD = {total * rate:.2f} {target}")
    if not live:
        print(YELLOW + "(offline - approximate rate used)" + RESET)


def change_password():
    if getpass.getpass("Current password: ") != credentials["password"]:
        print(RED + "Current password is wrong." + RESET)
        return
    new_password = getpass.getpass("New password: ")
    problems = check_password_strength(new_password)
    if problems:
        print(RED + "Weak password. Required:" + RESET)
        for p in problems:
            print("  -", p)
        return
    if getpass.getpass("Repeat new password: ") != new_password:
        print(RED + "Passwords do not match." + RESET)
        return
    credentials["password"] = new_password
    print(GREEN + "Password changed." + RESET)

def expenss_main():
    clear_screen()
    print_banner()
    if not login():
        print(RED + "Too many failed attempts. Goodbye." + RESET)
        return
    while True:
        clear_screen()
        print_banner()
        print_menu()
        choice = input("\nYour choice: ").strip()
        if choice == "8":
            print(GREEN + "Goodbye!" + RESET)
            break
        elif choice == "1":
            add_expense()
        elif choice == "2":
            show_expenses()
        elif choice == "3":
            show_stats()
        elif choice == "4":
            filter_by_category()
        elif choice == "5":
            show_chart()
        elif choice == "6":
            convert_total()
        elif choice == "7":
            change_password()
        else:
            print(RED + "Invalid choice. Enter a number between 1 and 8." + RESET)
        input("\nPress Enter to continue...")

def main():

    ### menu
    banner = '''WELCOME TO \033[1;34m
    ░█████████  ░██     ░██ ░████████     ░██████   ░██    ░██ 
    ░██     ░██  ░██   ░██  ░██    ░██   ░██   ░██   ░██  ░██  
    ░██     ░██   ░██ ░██   ░██    ░██  ░██     ░██   ░██░██   
    ░█████████     ░████    ░████████   ░██     ░██    ░███    
    ░██             ░██     ░██     ░██ ░██     ░██   ░██░██   
    ░██             ░██     ░██     ░██  ░██   ░██   ░██  ░██  
    ░██             ░██     ░█████████    ░██████   ░██    ░██
    \033[0m'''
    Menu="Menu:\n\t1. Calculator\n\t2. BMI\n\t3. Fibo\n\t4. Card_Number\n\t5. Pasword_Checker\n\t6.Weather\n\t7.CryptoPrice\n\t8.CryptoFigure\n\t9. Expenses_Tracker\n\t10. Exit"
    username = "admin"
    password = "1234"
    passcheak = 0
    logout = False

    while passcheak <3 :
        os.system("cls")
        print(banner)   
        user_ = input("username: ")
        pass_ = getpass.getpass("password: ")
        if (user_ == username and pass_ == password): 
            while True:
                os.system("cls")
                print(banner)
                print(Menu)     
                choice= int(input("Please choose a number between 1-10!:"))   
                match choice:
### Calc
                    case 1:
                        while True :
                            os.system("cls")
                            num1 = int(input("enter num1: "))
                            num2 = int(input("enter num2: "))
                            sum,mul,sub,div = Calc(num1,num2)
                            print("sum is:",sum)
                            print("mul is:" ,mul)
                            print("sub is:" ,sub)
                            print("div is:" ,div)
                            ex = input("\nFor back to menu press b (or any key to continue): ").strip().lower()
                            if ex == "b":
                                break
### BMI
                    case 2:
                        while True :
                            os.system("cls")
                            Weight = int(input("Please Enter Your Weight (kg): "))
                            Height = int(input("Please Enter your height (cm): "))
                            bmi,res= BMI(Weight,Height)
                            print("your bmi is:",bmi)
                            print("you are: ",res)
                            ex = input("\nFor back to menu press b (or any key to continue): ").strip().lower()
                            if ex == "b":
                                break
### Fibo
                    case 3:
                        while True :
                            os.system("cls")
                            fibo = int(input("Enter Fibo num: "))
                            res= Fibonachi(fibo)
                            result= str(res)
                            result= result.replace("[" , " ").replace("]" , " ")
                            print("your seri is:", result)
                            ex = input("\nFor back to menu press b (or any key to continue): ").strip().lower()
                            if ex == "b":
                                break
### CreditCard_Number
                    case 4:
                        while True :
                            os.system("cls")
                            credit = input("Please Enter Your creditcard Number : ").strip()  #5894631558120804
                            credit , bank = CreditCard(credit) 
                            print("your credit card number = ", credit)   
                            print("your bank is = ", bank)
                                      
                            ex = input("\nFor back to menu press b (or any key to continue): ").strip().lower()
                            if ex == "b":
                                break
### Password_Checker
                    case 5:
                        while True:
                            os.system("cls")
                            password =(input("please enter your Password: "))
                            score ,result ,emtiaz = PasswordCheacker(password)
                            print (f"{result} , score is:{score}, {emtiaz}")
                            ex= input("for back to menu enter b .(or press any key to continue)")
                            if ex == "b":
                                break    
### Weather
                    case 6:
                        while True:
                            os.system("cls")
                            # اول از همه اینترنت را چک می‌کنیم
                            print("Checking internet connection...")
                            if not has_internet():
                                print("No internet connection! Please check your network.")

                            else:
                                print("Connected to the internet!")

                            # کدهای گرفتن آب‌وهوا از سایت open-meteo
                            # گرفتن چند شهر از کاربر (جداشده با کاما)  
                            user_input = input("Enter city names in English, separated by commas (e.g. Tehran, Paris, Tokyo): ")
                            #List Comprehension
                            cities = [c.strip() for c in user_input.split(",") if c.strip()]    

                            if not cities:
                                print("No city entered!")
                                return  # از تابع و کل برنامه خارج میشه

                            temp_choice = input("Temperature unit: c (Celsius) or f (Fahrenheit) [c]: ").strip().lower()
                            if temp_choice == "f":
                                temp_unit = "fahrenheit"
                            else:
                                temp_unit = "celsius"

                                wind_choice = input("Wind speed unit: kmh, ms, mph or kn [kmh]: ").strip().lower()
                            if wind_choice in ["kmh", "ms", "mph", "kn"]:
                                wind_unit = wind_choice
                            else:
                                wind_unit = "kmh"

                            days_text = input("Number of forecast days (1-7) [3]: ").strip()
                            if days_text.isdigit() and 1 <= int(days_text) <= 7:
                                days = int(days_text)
                            else:
                                days = 3
                        
                            for city in cities:
                                process_city(city, temp_unit, wind_unit, days)

                            ex= input("for back to menu enter b .(or press any key to continue)")
                            if ex == "b":
                                break

### CryptoPrice 
                    case 7:
                        while True:
                            os.system("cls")
                            # اول از همه اینترنت را چک می‌کنیم
                            print("Checking internet connection...")
                            if not has_internet():
                                print("No internet connection! Please check your network.")
                            else:
                                print("Connected to the internet!")  

                            text = input("Enter cryptocurrency names separated by commas (e.g. bitcoin, ethereum, solana): ")
                            coins = []
                            for name in text.split(","):
                                coins.append(name.strip().lower())

                            data= get_crypto_price (coins)
                            print("Current prices:")
                            for coin in coins:
                                if coin in data:
                                    price = data[coin]["usd"]   #data.get("bitcoin").get("usd")
                                    print (f"price {coin} : ${price}")   #{price:,} >>  یعنی مبلغ رو سه تا سه تا جدا میکنه

                                else :
                                    print(f"{coin} not found!")                                              

                            ex= input("for back to menu enter b .(or press any key to continue)")
                            if ex == "b":
                                break


### CryptoFigure    
                    case 8: 
                        while True:
                            os.system("cls")
                            # اول از همه اینترنت را چک می‌کنیم
                            print("Checking internet connection...")
                            if not has_internet():
                                print("No internet connection! Please check your network.")
                            else:
                                print("Connected to the internet!")

                            symbol = input("Enter the coin symbol (e.g. BTC, ETH, SOL): ").strip().upper()
                            unit = input("Time unit - minutes (m), hours (h) or days (d): ").strip().lower()
                            amount_text = input("How many candles? (e.g. 60): ").strip()
                        
                            intervals = {"m": "1m", "h": "1h", "d": "1d"}
                            names = {"m": "minute", "h": "hour", "d": "day"}
                        
                            if unit not in intervals:
                                print("Unit must be m, h or d!")
                                return
                            if not amount_text.isdigit():
                                print("Please enter a whole number!")
                                return
                        
                            count = int(amount_text)
                            if count < 1 or count > 1000:
                                print("The number must be between 1 and 1000!")
                                return
                        
                            candles = get_candles(symbol, intervals[unit], count)
                        
                            if len(candles) == 0:
                                print("No data found! Check the coin symbol (e.g. BTC).")
                                return
                        
                            # درصد تغییر از اولین تا آخرین کندل
                            change = (candles[-1]["close"] - candles[0]["open"]) / candles[0]["open"] * 100
                        
                            title = f"{symbol}/USDT - {count} candles, 1 {names[unit]} each ({change:+.2f}%)"
                            file_name = f"{symbol}_candles.png"
                        
                            draw_chart(candles, title, file_name)
                            print(f"Chart saved as {file_name}")

                            ex= input("for back to menu enter b .(or press any key to continue)")
                            if ex == "b":
                                break
# Expenss_Tracker
                    case 9:
                        expenss_main()

### Exit
                    case 10:
                        logout = True
                        os.system("cls")
                        input("\033[1;32mGoodbye! PYBOX... \033[0m")
                        break  #خروج از منو 
### Invalid input
                    case _:
                        input("\033[1;31mYou must choose between 1-10! \033[0m\nPress Enter to try again... ")
            if logout:
                break    
### Wrong password    
        else:
            passcheak += 1
            input(f"\033[1;31mError! username or pasword is incorrect! you try {passcheak} time(s) of 3...\033[0m")



main()       