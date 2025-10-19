from flask import Flask, request, jsonify
import os
import re
from datetime import datetime

app = Flask(__name__)

# Fungsi utilitas dari kode Anda
def bersihkan_input_angka(teks):
    if teks is None:
        return 0.0
    teks = str(teks).strip()
    teks = re.sub(r"[^0-9]", "", teks)
    return float(teks) if teks else 0.0

def format_rupiah(angka):
    return f"{angka:,.0f}".replace(",", ".")

def hitung_pph21_progressive(penghasilan_neto_setahun):
    PTKP_TK0 = 54000000
    pkp = max(0, penghasilan_neto_setahun - PTKP_TK0)
    
    if pkp <= 0:
        return 0
    elif pkp <= 60000000:
        return pkp * 0.05
    elif pkp <= 250000000:
        return 3000000 + (pkp - 60000000) * 0.15
    elif pkp <= 500000000:
        return 34500000 + (pkp - 250000000) * 0.25
    elif pkp <= 5000000000:
        return 59500000 + (pkp - 500000000) * 0.30
    else:
        return 1545000000 + (pkp - 5000000000) * 0.35

# Route utama
@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return jsonify({"status": "WhatsApp Bot is running!", "version": "1.0"})
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"response": "❌ Tidak ada data received"})
        
        message = data.get('message', '').lower()
        phone = data.get('phone', 'unknown')
        
        print(f"Received from {phone}: {message}")
        
        # Process message
        if 'hitung lembur' in message:
            return handle_overtime(message)
        elif 'slip gaji' in message:
            return handle_salary_slip(message)
        elif 'help' in message or 'bantuan' in message:
            return handle_help()
        else:
            return handle_welcome()
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"response": f"❌ Error: {str(e)}"})

def handle_overtime(message):
    try:
        numbers = re.findall(r'\d+', message)
        
        if len(numbers) < 2:
            return jsonify({
                "response": """🤖 KALKULATOR LEMBUR

Format: hitung lembur [gaji] [jam]
Contoh: hitung lembur 5000000 3

Atau: hitung lembur [gaji] [jam] [uang_makan]
Contoh: hitung lembur 5000000 3 25000"""
            })
        
        gaji = bersihkan_input_angka(numbers[0])
        jam_lembur = int(numbers[1])
        uang_makan = bersihkan_input_angka(numbers[2]) if len(numbers) > 2 else 0
        
        # Validasi input
        if gaji <= 0:
            return jsonify({"response": "❌ Gaji harus lebih dari 0"})
        if jam_lembur < 0:
            return jsonify({"response": "❌ Jam lembur tidak boleh negatif"})
        
        # Perhitungan lembur
        gaji_per_jam = gaji / 173
        
        if jam_lembur == 0:
            total_lembur = 0
        elif jam_lembur == 1:
            total_lembur = 1.5 * gaji_per_jam
        else:
            total_lembur = (1.5 + (jam_lembur - 1) * 2) * gaji_per_jam
        
        # Uang makan
        total_uang_makan = uang_makan * jam_lembur
        total_pendapatan_lembur = total_lembur + total_uang_makan
        total_gaji_kotor = gaji + total_pendapatan_lembur
        
        # Format response
        response = f"""
💰 HASIL PERHITUNGAN LEMBUR
─────────────────────

📊 Gaji Pokok    : Rp {format_rupiah(gaji)}
⏰ Jam Lembur    : {jam_lembur} jam
💰 Gaji per Jam  : Rp {format_rupiah(gaji_per_jam)}

📈 RINCIAN LEMBUR:
"""
        
        if jam_lembur == 1:
            response += f"1 jam = 1.5 × Rp {format_rupiah(gaji_per_jam)}"
            response += f"\n= Rp {format_rupiah(total_lembur)}"
        elif jam_lembur > 1:
            response += f"Jam 1 = 1.5 × Rp {format_rupiah(gaji_per_jam)} = Rp {format_rupiah(1.5 * gaji_per_jam)}"
            response += f"\nJam 2+ = 2.0 × Rp {format_rupiah(gaji_per_jam)} × {jam_lembur-1} jam"
            response += f"\nTotal = Rp {format_rupiah(total_lembur)}"
        
        if uang_makan > 0:
            response += f"\n\n🍱 UANG MAKAN:"
            response += f"\n{jam_lembur} hari × Rp {format_rupiah(uang_makan)}"
            response += f"\n= Rp {format_rupiah(total_uang_makan)}"
        
        response += f"""
─────────────────────
💸 Total Lembur  : Rp {format_rupiah(total_pendapatan_lembur)}
💰 Total Gaji    : Rp {format_rupiah(total_gaji_kotor)}
─────────────────────

📝 *Berdasarkan regulasi lembur Indonesia*
        """
        
        return jsonify({"response": response})
        
    except Exception as e:
        return jsonify({"response": f"❌ Error perhitungan: {str(e)}"})

def handle_salary_slip(message):
    try:
        numbers = re.findall(r'\d+', message)
        
        if len(numbers) < 1:
            return jsonify({
                "response": """📋 SLIP GAJI LENGKAP

Format: slip gaji [gaji] [lembur] [potongan]
Contoh: slip gaji 5000000 500000 100000

• Gaji pokok (wajib)
• Lembur (opsional) 
• Potongan (opsional)"""
            })
        
        gaji_pokok = bersihkan_input_angka(numbers[0])
        lembur = bersihkan_input_angka(numbers[1]) if len(numbers) > 1 else 0
        potongan = bersihkan_input_angka(numbers[2]) if len(numbers) > 2 else 0
        
        # Perhitungan BPJS
        BATAS_MAX_JP = 10547400
        dasar_bpjs = gaji_pokok
        dasar_jp = min(dasar_bpjs, BATAS_MAX_JP)
        
        # BPJS Perusahaan
        jht_perusahaan = dasar_bpjs * 0.037
        jkk_perusahaan = dasar_bpjs * 0.0024  
        jkm_perusahaan = dasar_bpjs * 0.003
        jp_perusahaan = dasar_jp * 0.02
        bpjs_kes_perusahaan = dasar_bpjs * 0.04
        
        # Total pendapatan
        total_pendapatan = (gaji_pokok + lembur + jht_perusahaan + jkk_perusahaan + 
                          jkm_perusahaan + jp_perusahaan + bpjs_kes_perusahaan)
        
        # Potongan karyawan
        potongan_jht = dasar_bpjs * 0.02
        potongan_bpjs_kes = dasar_bpjs * 0.01
        potongan_jp = dasar_jp * 0.01
        
        total_potongan = (potongan_jht + potongan_bpjs_kes + potongan_jp + potongan)
        
        # Pajak
        sub_total = total_pendapatan - total_potongan
        pajak = sub_total * 0.015
        gaji_bersih = sub_total - pajak
        
        response = f"""
📋 SLIP GAJI LENGKAP
─────────────────────

📊 PENDAPATAN:
├─ Gaji Pokok          : Rp {format_rupiah(gaji_pokok)}
├─ Lembur              : Rp {format_rupiah(lembur)}
├─ JHT Perusahaan (3.7%): Rp {format_rupiah(jht_perusahaan)}
├─ JKK Perusahaan (0.24%): Rp {format_rupiah(jkk_perusahaan)}
├─ JKM Perusahaan (0.3%): Rp {format_rupiah(jkm_perusahaan)}
├─ JP Perusahaan (2%)  : Rp {format_rupiah(jp_perusahaan)}
└─ BPJS Kes (4%)       : Rp {format_rupiah(bpjs_kes_perusahaan)}

📈 TOTAL PENDAPATAN: Rp {format_rupiah(total_pendapatan)}

─────────────────────
💸 POTONGAN:
├─ JHT Karyawan (2%)   : Rp {format_rupiah(potongan_jht)}
├─ BPJS Kes (1%)       : Rp {format_rupiah(potongan_bpjs_kes)}
├─ JP Karyawan (1%)    : Rp {format_rupiah(potongan_jp)}
├─ Potongan Lain       : Rp {format_rupiah(potongan)}
└─ Pajak (1.5%)        : Rp {format_rupiah(pajak)}

📉 TOTAL POTONGAN: Rp {format_rupiah(total_potongan + pajak)}

─────────────────────
💰 GAJI BERSIH: Rp {format_rupiah(gaji_bersih)}
─────────────────────
        """
        
        return jsonify({"response": response})
        
    except Exception as e:
        return jsonify({"response": f"❌ Error slip gaji: {str(e)}"})

def handle_help():
    response = """
🤖 BOT KALKULATOR GAJI
─────────────────────

📋 PERINTAH:

1. 🕒 HITUNG LEMBUR
   • hitung lembur [gaji] [jam]
   • Contoh: hitung lembur 5000000 3

2. 📊 SLIP GAJI LENGKAP
   • slip gaji [gaji] [lembur] [potongan]  
   • Contoh: slip gaji 5000000 500000 100000

3. ℹ️  BANTUAN
   • help - Menu ini

─────────────────────
    """
    return jsonify({"response": response})

def handle_welcome():
    response = """
👋 SELAMAT DATANG!

Saya adalah Bot Kalkulator Gaji yang siap membantu:

🕒 Hitung lembur sesuai regulasi Indonesia
📊 Buat slip gaji lengkap dengan BPJS & pajak  
💰 Hitung gaji bersih

Ketik *help* untuk melihat menu lengkap.
    """
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
