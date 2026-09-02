# SIGAP Meter

**Sistem Informasi Gangguan dan Analisis Perangkat Meter**

Dashboard Streamlit untuk menggabungkan banyak file Excel bulanan dan menganalisis gangguan kWh meter pada tingkat UP3 dan ULP.

## Fitur

- Unggah beberapa file Excel, XLS, atau CSV sekaligus.
- Validasi 24 kolom wajib pada setiap file.
- Penggabungan data dan penghapusan baris identik secara otomatis.
- Filter global berdasarkan tahun, bulan, UP3, ULP, dan petugas.
- KPI total gangguan, jenis layanan, fasa, merek dominan, dan petugas teraktif.
- Ringkasan UP3 dan perbandingan antar ULP.
- Analisis merek meter dan penyebab kerusakan.
- Leaderboard produktivitas pencatatan petugas.
- Ekspor laporan Excel dengan beberapa sheet ringkasan.

## Struktur Proyek

```text
SIGAP_Meter_Dashboard/
├── app.py
├── pages/
│   ├── 2_Ringkasan_UP3.py
│   ├── 3_Analisis_ULP.py
│   ├── 4_Detail_Kerusakan.py
│   ├── 5_Leaderboard_Petugas.py
│   └── 6_Unggah_Ekspor.py
├── src/
│   ├── analytics.py
│   ├── data_loader.py
│   ├── export_report.py
│   ├── preprocessor.py
│   ├── ui.py
│   └── visualizer.py
├── assets/pln_logo.svg
├── .streamlit/config.toml
├── mulai_dashboard.bat
└── requirements.txt
```

## Menjalankan di Windows

Bila ingin cara paling mudah, klik dua kali file `mulai_dashboard.bat`. File tersebut akan membuat virtual environment, memasang dependensi, dan menjalankan dashboard secara otomatis.

Untuk menjalankan secara manual, buka PowerShell di dalam folder proyek, kemudian jalankan:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Jika PowerShell menolak aktivasi virtual environment, jalankan satu kali:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Setelah server aktif, buka alamat yang ditampilkan Streamlit, biasanya `http://localhost:8501`.

## Cara Menggunakan

1. Buka bagian **Manajemen File** pada sidebar.
2. Pilih seluruh file Excel bulanan yang ingin dianalisis.
3. Tunggu proses validasi dan penggabungan selesai.
4. Buka menu **Ringkasan UP3** atau halaman analisis lainnya.
5. Gunakan menu **Unggah Data & Ekspor** untuk memeriksa kualitas data dan mengunduh laporan.

## Kolom Wajib

File harus memiliki kolom berikut:

```text
TANGGAL INPUT, JAM INPUT, NAMA PELAPOR, ALAMAT, NO. HP,
ID PELANGGAN, PENGAWATAN, MERK, JENIS LAYANAN, NO. METER,
STAN, DAYA, NO. STROOK DG, PROGRAM GANTI METER, PETUGAS,
KOORDINAT, PENYEBAB KERUSAKAN, ARUS, TEGANGAN, STATUS,
STATUS PROSES, KODE ULP, NAMA ULP, NAMA UP3
```

Nama kolom akan dibersihkan dari spasi tambahan dan perbedaan huruf kapital. File yang tidak memenuhi struktur akan ditandai dan tidak ikut digabungkan.

## Catatan Data

- Leaderboard menunjukkan jumlah input laporan, bukan penilaian kualitas kerja petugas.
- Data pribadi seperti nama pelapor, nomor HP, alamat, dan koordinat tidak ditampilkan pada halaman dashboard.
- Ekspor detail tidak menyertakan nama pelapor, nomor HP, alamat, atau koordinat.
- Grafik tren bulanan akan lebih informatif setelah file dari beberapa bulan diunggah.
