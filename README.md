# Milijon Railway Panel

پنل مدیریت VPN/Proxy حرفه‌ای - نسخه ۳.۰

## ویژگی‌ها

### پروتکل‌های پشتیبانی شده
- VLESS
- VMess
- Trojan
- Shadowsocks

### ترانسپورت‌های پشتیبانی شده
- WebSocket (WS)
- gRPC
- HTTP/2 (H2)
- TCP

### ترکیب‌های پروتکل + ترانسپورت
- VLESS + WebSocket (WS)
- VMess + WebSocket (WS)
- Trojan + WebSocket (WS)
- Shadowsocks + v2ray-plugin (WebSocket)
- VLESS + gRPC
- VMess + gRPC
- Trojan + gRPC
- VLESS + HTTP/2 (H2)
- VMess + HTTP/2 (H2)
- Shadowsocks + TCP
- Trojan + TCP
- VLESS + TCP

### کلاینت‌های پشتیبانی شده
- v2rayNG (Android)
- v2rayN (Windows)
- V2RayU (macOS)
- Shadowrocket (iOS)
- NekoBox (Android)
- NekoBoxPlus (Android)
- Exclave (iOS)
- Clash Meta (Cross-platform)
- sing-box (Cross-platform)
- Hiddify (Cross-platform)
- Streisand (iOS)
- V2RayTun (iOS)

### امکانات پنل
- داشبورد با آمار کامل
- مدیریت اینباندها با تنظیمات پیشرفته
- مدیریت کاربران پیشرفته (حجم، انقضا، سابلینک)
- سابلینک خودکار (عمومی، Clash Meta، sing-box)
- مدیریت سرورها با مانیتورینگ
- صفحه وضعیت عمومی
- تنظیمات پیشرفته (پنل، امنیت، سابلینک، تلگرام)
- پشتیبانی از QR Code
- رابط کاربری فارسی RTL

## استقرار روی Railway

1. این ریپو را به Railway متصل کنید
2. متغیرهای محیطی زیر را تنظیم کنید:
   - `SUPABASE_URL` - آدرس Supabase
   - `SUPABASE_ANON_KEY` - کلید anon
   - `PORT` - پورت (پیش‌فرض 2095)
3. Railway به‌صورت خودکار Dockerfile را build و deploy می‌کند

## تکنولوژی
- Python 3.12 + Flask
- Supabase (PostgreSQL)
- Gunicorn (production server)
- Tailwind CSS (frontend)
