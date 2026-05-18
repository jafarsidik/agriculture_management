# ============================================================		
#  Scheduled Jobs		
#  Place in: agriculture_management/agriculture_management/		
#            tasks.py		
#		
#  Register in hooks.py:		
#    scheduler_events = {		
#        "daily": [		
#            "agriculture_management.tasks.check_maintenance_due",		
#            "agriculture_management.tasks.fetch_weather_data",		
#            "agriculture_management.tasks.check_low_stock",		
#        ]		
#    }		
# ============================================================		

import frappe		
from frappe import _		
from frappe.utils import today, add_days, getdate		
		
		
# ── 1. Maintenance Due Alert ─────────────────────────────────		
def check_maintenance_due():		
    """		
    Runs daily. Finds equipment where next_maintenance is within 14 days		
    and auto-creates a draft Equipment Maintenance if none exists.		
    """		
    threshold = add_days(today(), 14)		
		
    equipment_list = frappe.get_all(		
        "Farm Equipment",		
        filters=[
            ["status", "!=", "Retired"],
            ["next_maintenance", "<=", threshold],
            ["next_maintenance", "is", "set"],
        ]
        fields=["name", "equipment_name", "next_maintenance", "assigned_farm"]		
    )		
		
    for eq in equipment_list:		
        # Skip if a scheduled/draft maintenance already exists		
        existing = frappe.db.exists("Equipment Maintenance", {		
            "equipment": eq.name,		
            "status":    ["in", ["Draft", "Scheduled"]],		
            "docstatus": ["!=", 2]		
        })		
        if existing:		
            continue		
		
        # Create draft maintenance		
        doc = frappe.new_doc("Equipment Maintenance")		
        doc.update({		
            "equipment":         eq.name,		
            "maintenance_type":  "Preventive",		
            "scheduled_date":    eq.next_maintenance,		
            "status":            "Scheduled",		
        })		
        doc.insert(ignore_permissions=True)		
		
        # Send email notification		
        settings = frappe.get_single("Agriculture Settings")		
        if settings.notif_email:		
            frappe.sendmail(		
                recipients=settings.notif_email,		
                subject=f"[Agriculture] Maintenance Due: {eq.equipment_name}",		
                message=f"""		
                    <p>Equipment <b>{eq.equipment_name}</b> is due for maintenance		
                    on <b>{eq.next_maintenance}</b>.</p>		
                    <p>A draft maintenance record has been created:		
                    <a href="/app/equipment-maintenance/{doc.name}">{doc.name}</a></p>		
                """,		
                now=True		
            )		
		
    frappe.logger().info(		
        f"[check_maintenance_due] Processed {len(equipment_list)} equipment records."		
    )		
		
		
# ── 2. Low Stock Alert ───────────────────────────────────────		
def check_low_stock():		
    """		
    Runs daily. Sends one summary email if any inputs are Low / Out of Stock.		
    """		
    low_items = frappe.get_all(		
        "Input Stock Balance",		
        filters={"stock_status": ["in", ["Low", "Out of Stock"]]},		
        fields=["farm", "input_item", "current_stock", "min_stock", "stock_status"]		
    )		
		
    if not low_items:		
        return		
		
    settings = frappe.get_single("Agriculture Settings")		
    if not settings.notif_email:		
        return		
		
    rows = "".join(		
        f"<tr><td>{i.farm}</td><td>{i.input_item}</td>"		
        f"<td>{i.current_stock}</td><td>{i.min_stock}</td>"		
        f"<td><b style='color:{'red' if i.stock_status=='Out of Stock' else 'orange'}'>"		
        f"{i.stock_status}</b></td></tr>"		
        for i in low_items		
    )		
		
    frappe.sendmail(		
        recipients=settings.notif_email,		
        subject=f"[Agriculture] Low Stock Alert — {len(low_items)} item(s)",		
        message=f"""		
            <p>The following farm inputs are running low:</p>		
            <table border='1' cellpadding='5' style='border-collapse:collapse'>		
                <tr><th>Farm</th><th>Input</th><th>Current</th><th>Min Stock</th><th>Status</th></tr>		
                {rows}		
            </table>		
            <p>Please create a Purchase Order to replenish stock.</p>		
        """,		
        now=True		
    )		
    frappe.logger().info(		
        f"[check_low_stock] Alert sent for {len(low_items)} low-stock items."		
    )		
		
		
# ── 3. Auto-fetch Weather Data (OpenWeatherMap) ──────────────		
def fetch_weather_data():		
    """		
    Runs daily. Fetches weather for all Active farms using OpenWeatherMap API.		
    Requires: Agriculture Settings.weather_api_key and farms with lat/lon set.		
    """		
    import requests		
		
    settings = frappe.get_single("Agriculture Settings")		
    if not getattr(settings, "enable_weather", False):		
        return		
		
    api_key = getattr(settings, "weather_api_key", None)		
    if not api_key:		
        frappe.logger().warning("[fetch_weather_data] No weather_api_key in Agriculture Settings.")		
        return		
		
    farms = frappe.get_all(		
        "Farm",		
        filters={"status": "Active"},		
        fields=["name", "farm_name", "latitude", "longitude"]		
    )		
		
    for farm in farms:		
        if not farm.latitude or not farm.longitude:		
            continue		
		
        # Skip if today's log already exists		
        if frappe.db.exists("Weather Log", {"farm": farm.name, "log_date": today()}):		
            continue		
		
        try:		
            url = (		
                f"https://api.openweathermap.org/data/2.5/weather"		
                f"?lat={farm.latitude}&lon={farm.longitude}"		
                f"&appid={api_key}&units=metric"		
            )		
            resp = requests.get(url, timeout=10)		
            data = resp.json()		
		
            if resp.status_code != 200:		
                frappe.logger().warning(		
                    f"[fetch_weather_data] API error for {farm.name}: {data.get('message')}"		
                )		
                continue		
		
            main    = data.get("main", {})		
            wind    = data.get("wind", {})		
            weather = data.get("weather", [{}])[0]		
            rain    = data.get("rain", {}).get("1h", 0)		
		
            # Map OWM condition to Select options		
            condition_map = {		
                "Clear":       "Sunny",		
                "Clouds":      "Partly Cloudy",		
                "Rain":        "Rainy",		
                "Drizzle":     "Rainy",		
                "Thunderstorm":"Stormy",		
                "Snow":        "Partly Cloudy",		
                "Mist":        "Foggy",		
                "Fog":         "Foggy",		
            }		
            owm_main  = weather.get("main", "")		
            condition = condition_map.get(owm_main, "Partly Cloudy")		
		
            log = frappe.new_doc("Weather Log")		
            log.update({		
                "farm":              farm.name,		
                "log_date":          today(),		
                "temp_min":          main.get("temp_min"),		
                "temp_max":          main.get("temp_max"),		
                "humidity":          main.get("humidity"),		
                "rainfall":          rain,		
                "wind_speed":        wind.get("speed", 0) * 3.6,   # m/s → km/h		
                "weather_condition": condition,		
                "data_source":       "OpenWeather API",		
            })		
            log.insert(ignore_permissions=True)		
		
        except Exception as e:		
            frappe.logger().error(f"[fetch_weather_data] Failed for {farm.name}: {e}")		
		
    frappe.logger().info(f"[fetch_weather_data] Completed for {len(farms)} farms.")		
		
