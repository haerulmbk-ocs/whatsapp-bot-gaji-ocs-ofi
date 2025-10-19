from flask import Flask, request, jsonify
import os
import re

app = Flask(__name__)

def bersihkan_input_angka(teks):
    if teks is None:
        return 0.0
    teks = str(teks).strip()
    teks = re.sub(r"[^0-9]", "", teks)
    return float(teks) if teks else 0.0

def format_rupiah(angka):
    return f"{angka:,.0f}".replace(",", ".")

@app.route('/', methods=['GET'])
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 WhatsApp Bot Kalkulator Gaji</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 10px; }
            .url-box { background: white; padding: 15px; border-radius: 5px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 WhatsApp Bot Kalkulator Gaji</h1>
            <p><strong>Status:</strong> ✅ <span style="color: green;">AKTIF</span></p>
            
            <div class="url-box">
                <h3>🔗 Webhook URL:</h3>
                <code>https://whatsapp-bot-gaji-ocs-ofi-haerulmbk123.replit.app/webhook</code>
            </div>
            
            <h3>📋 Cara Test:</h3>
            <pre>
curl -X POST https://whatsapp-bot-gaji-ocs-ofi-haerulmbk123.replit.app/webhook \\
  -H "Content-Type: application/json" \\
  -d '{"message": "hitung lembur 5000000 3"}'
            </pre>
            
            <p><strong>Perintah yang tersedia:</strong></p>
            <ul>
                <li>hitung lembur [gaji] [jam]</li>
                <li>slip gaji [gaji] [lembur] [potongan]</li>
                <li>help</li>
            </ul>
        </div>
    </body>
    </html>
    """

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return jsonify({
            "status": "WhatsApp Bot Ready!",
            "author": "Kalkulator Gaji Indonesia", 
            "webhook_url": "https://whatsapp-bot-gaji-ocs-ofi-haerulmbk123.replit.app/webhook",
            "usage": "Send POST request with JSON: {'message': 'hitung lembur 5000000 3'}"
        })
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"response": "❌ Tidak ada data received"})
        
        message = data.get('message', '').lower()
        
        if 'hitung lembur' in message:
            return handle_overtime(message)
        elif 'slip gaji' in message:
            return handle_salary_slip(message)
        elif 'help' in message:
            return handle_help()
        elif 'ping' in message:
            return jsonify({"response": "🏓 Pong! Bot aktif!"})
        else:
            return handle_welcome()
            
    except Exception as e:
        return jsonify({"response": f"❌ Error: {str(e)}"})

def handle_overtime(message):
    try:
        numbers = re.findall(r'\d+', message)
        
        if len(numbers) < 2:
            return jsonify({
                "response": """🤖 KALKULATOR LEMBUR

Format: hitung lembur [gaji] [jam]
Contoh: hitung lembur 5000000 3"""
            })
        
        gaji = bersihkan_input_angka(numbers[0])
        jam_lembur = int(numbers[1])
        
        gaji_per_jam = gaji / 173
        
        if jam_lembur == 0:
            total_lembur = 0
        elif jam_lembur == 1:
            total_lembur = 1.5 * gaji_per_jam
        else:
            total_lembur = (1.5 + (jam_lembur - 1) * 2) * gaji_per_jam
        
        total_gaji = gaji + total_lembur
        
        response = f"""
💰 HASIL PERHITUNGAN LEMBUR

📊 Gaji Pokok: Rp {format_rupiah(gaji)}
⏰ Jam Lembur: {jam_lembur} jam  
💰 Gaji per Jam: Rp {format_rupiah(gaji_per_jam)}
💸 Total Lembur: Rp {format_rupiah(total_lembur)}
📈 Total Gaji: Rp {format_rupiah(total_gaji)}
        """
        
        return jsonify({"response": response})
        
    except Exception as e:
        return jsonify({"response": f"❌ Error: {str(e)}"})

def handle_salary_slip(message):
    try:
        numbers = re.findall(r'\d+', message)
        
        if len(numbers) < 1:
            return jsonify({
                "response": """📋 SLIP GAJI

Format: slip gaji [gaji] [lembur] [potongan]
Contoh: slip gaji 5000000 500000 100000"""
            })
        
        gaji = bersihkan_input_angka(numbers[0])
        lembur = bersihkan_input_angka(numbers[1]) if len(numbers) > 1 else 0
        potongan = bersihkan_input_angka(numbers[2]) if len(numbers) > 2 else 0
        
        # Perhitungan sederhana
        bpjs_perusahaan = gaji * 0.04
        jht_perusahaan = gaji * 0.037
        
        total_pendapatan = gaji + lembur + bpjs_perusahaan + jht_perusahaan
        potongan_jht = gaji * 0.02
        potongan_bpjs = gaji * 0.01
        
        total_potongan = potongan_jht + potongan_bpjs + potongan
        pajak = (total_pendapatan - total_potongan) * 0.015
        gaji_bersih = total_pendapatan - total_potongan - pajak
        
        response = f"""
📋 SLIP GAJI SEDERHANA

📊 PENDAPATAN:
├─ Gaji Pokok: Rp {format_rupiah(gaji)}
├─ Lembur: Rp {format_rupiah(lembur)}
├─ BPJS Perusahaan: Rp {format_rupiah(bpjs_perusahaan)}
└─ JHT Perusahaan: Rp {format_rupiah(jht_perusahaan)}

💸 POTONGAN:
├─ JHT Karyawan: Rp {format_rupiah(potongan_jht)}
├─ BPJS Karyawan: Rp {format_rupiah(potongan_bpjs)}
├─ Potongan Lain: Rp {format_rupiah(potongan)}
└─ Pajak: Rp {format_rupiah(pajak)}

💰 GAJI BERSIH: Rp {format_rupiah(gaji_bersih)}
        """
        
        return jsonify({"response": response})
        
    except Exception as e:
        return jsonify({"response": f"❌ Error: {str(e)}"})

def handle_help():
    response = """
🤖 BOT KALKULATOR GAJI

PERINTAH:
• hitung lembur [gaji] [jam]
• slip gaji [gaji] [lembur] [potongan]  
• help - Menu bantuan
• ping - Cek status
    """
    return jsonify({"response": response})

def handle_welcome():
    response = """
👋 SELAMAT DATANG!

Bot Kalkulator Gaji siap membantu:
• Hitung lembur
• Slip gaji lengkap

Ketik 'help' untuk menu
    """
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
