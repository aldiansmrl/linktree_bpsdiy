# 🌲 Linktree Clone Web App dengan Admin Panel

Aplikasi web *link-in-bio* (seperti Linktree / Beacons) modern, responsif, dan ringan yang dilengkapi dengan **Admin Panel lengkap** untuk mengelola profil, menambah/mengedit/menghapus tautan, mengatur tema visual, serta memantau statistik jumlah klik.

Dibuat menggunakan **Python 3**, **Tornado Framework**, dan database **SQLite** bawaan (tanpa perlu install database server terpisah).

---

## 🚀 Fitur Unggulan

### 1. Halaman Publik (Tampilan Linktree)
- 📱 **Mobile-First & Responsif**: Tampilan rapi dan nyaman dibuka dari smartphone maupun layar desktop.
- 🎨 **7 Pilihan Tema Visual**:
  - *BPS Pastel* (Warna khas logo Badan Pusat Statistik: Biru, Hijau, dan Oranye dalam gradasi lembut pastel)
  - *Modern Glassmorphism* (Efek frosted glass dengan gradasi warna modern)
  - *Modern Dark* (Nuansa gelap elegan OLED & zinc)
  - *Cyberpunk Neon* (Sentuhan ungu elektrik & aksen cyan glowing)
  - *Sunset Gradient* (Gradasi hangat peach & magenta)
  - *Emerald Luxury* (Nuansa hijau zamrud & emas)
  - *Minimalist Clean* (Tampilan bersih hitam & putih gaya editorial)
- ✨ **Link Highlight**: Opsi untuk menyorot link penting dengan animasi *glowing pulse*.
- 🏷️ **Kategori / Grup Link**: Mengelompokkan tautan berdasarkan kategori (contoh: *Featured*, *Sosial*, *Proyek*, *Toko*).
- 🌟 **Ikon Resmi Vektor & Kustom**: Ikon resmi SVG berkualitas tajam untuk YouTube, Instagram, X (Twitter), Facebook, Website resmi, WhatsApp, dan Logo BPS.
- 💬 **Bar Media Sosial Lengkap**: Tombol profil YouTube, Instagram, X, Facebook, Website, WhatsApp, GitHub, LinkedIn, TikTok, dan Email.
- 📤 **Fitur Bagikan & QR Code**: Memungkinkan pengunjung langsung memindai QR Code atau menyalin URL dengan satu klik.

### 2. Admin Panel (`/admin`)
- 🔐 **Autentikasi Aman**: Login berbasis sesi dengan proteksi secure cookie HMAC dan enkripsi password PBKDF2-SHA256.
- 🎨 **Manajemen Aset Ikon Lengkap**:
  - **Ikon Brand Resmi (1-Klik)**: YouTube, Instagram, X, Facebook, Website, WhatsApp, Logo BPS.
  - **Unggah Ikon Sendiri**: Bisa upload gambar/SVG dari komputer (tersimpan ke server).
  - **URL Luar**: Tempel link gambar/ikon apa saja dari internet (Flaticon, Wikimedia, CDN).
  - **Emoji Picker**: Kategori lengkap statistik, bisnis, dan sosial.
- ➕ **Tambah, Edit & Hapus Link**: Form modal intuitif dengan live icon preview.
- 🔄 **Ubah Urutan Link (Reorder)**: Bisa geser langsung (*drag & drop*) atau klik tombol panah ⬆️ / ⬇️.
- 👁️ **Toggle Aktif / Nonaktif**: Sembunyikan atau tampilkan tautan tanpa perlu menghapusnya.
- 🖼️ **Pengaturan Profil & Foto**: Unggah foto profil langsung dari komputer atau gunakan URL gambar.
- 📊 **Statistik & Analisis Klik**:
  - Total pengunjung yang mengklik setiap link secara *real-time*.
  - Top 5 link paling populer.
  - Log riwayat 10 klik terakhir.
- 📱 **Live Mobile Preview**: Layar simulator smartphone langsung di dashboard admin yang otomatis memperbarui tampilan saat ada perubahan.
- 🔒 **Ganti Password**: Menu khusus untuk memperbarui kata sandi admin kapan saja.

---

## 🛠️ Cara Menjalankan

### Persyaratan:
- Python 3.10+ (sudah tersedia di sistem Anda)
- Library `tornado` (sudah terpasang)

### Langkah Menjalankan:

Buka terminal dan jalankan:

```bash
cd /Users/aldian/.gemini/antigravity/scratch/linktree-app
./start.sh
```

Atau menggunakan perintah Python langsung:

```bash
python3 app.py --port 8000
```

---

## 🔑 Akses URL & Kredensial Default

Setelah server berjalan:

| Halaman | URL |
| :--- | :--- |
| **Halaman Publik (Linktree)** | [http://localhost:8000/](http://localhost:8000/) |
| **Admin Panel** | [http://localhost:8000/admin](http://localhost:8000/admin) |
| **Halaman Login** | [http://localhost:8000/login](http://localhost:8000/login) |

**Kredensial Default Admin:**
- **Username**: `admin`
- **Password**: `admin123`

*(Anda dapat mengganti password ini di tab **Keamanan** pada Admin Panel).*

---

## 📁 Struktur Direktori

```text
linktree-app/
├── app.py              # Server aplikasi utama Tornado & routing API
├── database.py         # Lapisan database SQLite & helper model
├── start.sh            # Skrip cepat menjalankan aplikasi
├── README.md           # Dokumentasi lengkap
├── data/
│   └── linktree.db     # File database SQLite otomatis terbuat
├── templates/
│   ├── base.html       # Kerangka HTML utama
│   ├── index.html      # Halaman profil publik Linktree
│   ├── login.html      # Halaman login admin
│   └── admin.html      # Dashboard pengelolaan link & live preview
└── static/
    ├── css/
    │   └── custom.css  # Desain tema, animasi, dan komponen UI
    ├── js/
    │   ├── admin.js    # Logika CRUD, drag-and-drop, dan toast admin
    │   └── qrcode.min.js # Komponen pembuat QR Code
    └── uploads/        # Direktori foto profil yang diunggah
```
