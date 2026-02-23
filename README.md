<div align="center">

```
    ██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗
    ██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║
    ██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║
    ██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║
    ██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║
    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝
    ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
    ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
    ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
    ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
    ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
    ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
```

### 👻 Mobile Pentest & OSINT Framework

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20|%20Windows%20|%20Termux-red?style=for-the-badge)](#)
[![GitHub Stars](https://img.shields.io/github/stars/c0d3s3cl4b/PhantomRecon?style=for-the-badge&color=gold)](https://github.com/c0d3s3cl4b/PhantomRecon)

**PhantomRecon**, modüler ve güçlü bir mobil pentest & OSINT (Open Source Intelligence) framework'üdür. Keşif, bilgi toplama ve güvenlik analizi için tasarlanmış 8 farklı modül içerir.

_Shadows don't leave fingerprints_ 🕵️

---

</div>

## 🔥 Özellikler

|          Modül          | Açıklama                              | Öne Çıkan                               |
| :---------------------: | :------------------------------------ | :-------------------------------------- |
|   📱 **Phone Lookup**   | Telefon numarası OSINT analizi        | Ülke, operatör, hat tipi, zaman dilimi  |
|    🌐 **IP Lookup**     | IP adresi bilgi toplama & geolocation | ISP, konum, koordinat, VPN tespiti      |
|   📧 **Email OSINT**    | Email araştırma & doğrulama           | MX kontrol, itibar, veri ihlali tespiti |
| 👤 **Username Search**  | 25+ platformda kullanıcı adı tarama   | Multi-threaded, hızlı tarama            |
|   🔍 **WHOIS Lookup**   | Domain WHOIS bilgi sorgusu            | Registrar, tarihler, NS kayıtları       |
| 🌍 **Subdomain Finder** | Subdomain keşfi & enumeration         | crt.sh + DNS brute-force (80+ kelime)   |
|   🔓 **Port Scanner**   | TCP port tarama & servis tespiti      | Banner grabbing, Top 100, özel aralık   |
|  📸 **EXIF Extractor**  | Görsel metadata çıkarma               | GPS koordinat, kamera bilgisi           |

## ⚡ Hızlı Kurulum

### Gereksinimler

- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)

### Linux / macOS

```bash
git clone https://github.com/c0d3s3cl4b/PhantomRecon.git
cd PhantomRecon
pip install -r requirements.txt
python phantomrecon.py
```

### Windows

```powershell
git clone https://github.com/c0d3s3cl4b/PhantomRecon.git
cd PhantomRecon
pip install -r requirements.txt
python phantomrecon.py
```

### Termux (Android) 📱

```bash
pkg update && pkg upgrade
pkg install python git
git clone https://github.com/c0d3s3cl4b/PhantomRecon.git
cd PhantomRecon
pip install -r requirements.txt
python phantomrecon.py
```

## 📂 Proje Yapısı

```
PhantomRecon/
├── phantomrecon.py          # Ana giriş noktası
├── requirements.txt         # Python bağımlılıkları
├── README.md                # Dokümantasyon
├── LICENSE                  # MIT Lisansı
├── core/
│   ├── __init__.py
│   ├── banner.py            # ASCII banner & UI bileşenleri
│   └── utils.py             # Yardımcı fonksiyonlar
├── modules/
│   ├── __init__.py
│   ├── phone_lookup.py      # Telefon OSINT
│   ├── ip_lookup.py         # IP bilgi toplama
│   ├── email_osint.py       # Email OSINT
│   ├── username_search.py   # Kullanıcı adı tarama
│   ├── whois_lookup.py      # WHOIS sorgusu
│   ├── subdomain_finder.py  # Subdomain keşfi
│   ├── port_scanner.py      # Port tarayıcı
│   └── exif_extractor.py    # EXIF metadata çıkarma
└── reports/                 # Otomatik oluşturulan raporlar
```

## 🛡️ Sorumluluk Reddi

Bu araç **yalnızca eğitim amaçlı** ve **yasal izinli güvenlik testleri** için geliştirilmiştir. Aracı kullanarak yapılan tüm eylemlerden kullanıcı sorumludur. Yetkisiz sistemlere erişim **yasa dışıdır**.

> **Uyarı:** Bu aracı yalnızca kendi sistemleriniz veya izin aldığınız sistemler üzerinde kullanın.

## 📊 API Kaynakları

| Servis      | Kullanım                | API Anahtarı  |
| ----------- | ----------------------- | ------------- |
| ip-api.com  | IP Geolocation          | ❌ Gerekmiyor |
| crt.sh      | SSL Sertifika Şeffaflık | ❌ Gerekmiyor |
| emailrep.io | Email İtibar            | ❌ Ücretsiz   |

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/yeni-modul`)
3. Commit edin (`git commit -m 'Yeni modül eklendi'`)
4. Push edin (`git push origin feature/yeni-modul`)
5. Pull Request açın

## 📜 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

## 📬 İletişim

- **GitHub:** [@c0d3s3cl4b](https://github.com/c0d3s3cl4b)

---

<div align="center">

**⭐ Projeyi beğendiysen yıldız bırakmayı unutma! ⭐**

_Made with 💀 by c0d3s3cl4b_

</div>
