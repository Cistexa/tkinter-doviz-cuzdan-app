#python 3.12
import tkinter as tk
from tkinter import ttk, messagebox
import http.client
import json
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime


# HTTP baglantisi kurma
conn = http.client.HTTPSConnection("api.collectapi.com")

# istek başliklarini (headers) ayarlama
headers = {
    'content-type': "application/json",
    'authorization': "apikey **************"
}

# GET istegi gönderme
conn.request("GET", "/economy/currencyToAll?int=10&base=USD", headers=headers)



# Yaniti alma
res = conn.getresponse()
data = res.read()

# Yanit verisini JSON formatinda parse etme
data = json.loads(data)

# Döviz turlerinin isimlerini bir listeye ekleme
currency_names = [currency['code'] for currency in data['result']['data']]
conn.close()
# conn.request("GET", "/economy/goldPrice", headers=headers)
# response = conn.getresponse()
# response_read=response.read()
# data_2=json.loads(response_read)
# currency_names.append(gold['name'] for gold in data_2['result'])
#Dövizleri adlarini apiden çekemedim manuel ekledim
altinandusd_name=[  "USD","ONS Altin","Çeyrek Altin", "Yarim Altin","Tam Altin","Cumhuriyet Altini","Gremse Altin","Has Altin","Çeyrek Altin Eski","Yarim Altin Eski","Tam Altin Eski","22 Ayar Bilezik","Gremse Altin Eski","Reşat Lira Altin","Reşat ikibuçuk Altin","Reşat Beşibiryerde","Ata Altin","Ziynet Altin","14 Ayar Altin","Beşli Altin","18 Ayar Altin","ikibuçuk Altin","Hamit Altin","ONS EUR","Altin Gumuş","Gumuş"]
currency_names.extend(altinandusd_name)
print(currency_names)
#Çekilen veriler 
# Baglantiyi kapatma
conn.close()


api_key = "******************"

def dovizcekme(api_key):
    conn = http.client.HTTPSConnection("api.collectapi.com")
    headers = {
        "authorization": f"apikey {api_key}",
        "content-type": "application/json"
    }
    conn.request("GET", "/economy/allCurrency", headers=headers)
    response = conn.getresponse()
    if response.status == 200:
        data = response.read()
        return json.loads(data)
    else:
        print("Döviz verilerini çekerken hata oluştu:", response.status, response.reason)
        return None

def altincekme(api_key):
    conn = http.client.HTTPSConnection("api.collectapi.com")
    headers = {
        "authorization": f"apikey {api_key}",
        "content-type": "application/json"
    }
    conn.request("GET", "/economy/goldPrice", headers=headers)
    response = conn.getresponse()
    if response.status == 200:
        data = response.read()
        return json.loads(data)
    else:
        print("Altin verilerini çekerken hata oluştu:", response.status, response.reason)
        return None

def veritabani():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE iF NOT EXiSTS transactions (
            id iNTEGER PRiMARY KEY AUTOiNCREMENT,
            tur TEXT,
            miktar REAL,
            tarih TEXT,
            kaldirildi iNTEGER DEFAULT 0
        )
    ''')
    conn.commit()


    cursor.execute("PRAGMA table_info(transactions)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'kaldirildi' not in columns:
        cursor.execute('ALTER TABLE transactions ADD COLUMN kaldirildi iNTEGER DEFAULT 0')
        conn.commit()

    conn.close()

def varlikgir(asset_type, amount):
    # Varlik turu geçerli mi kontrolu
    if asset_type not in currency_names:
        messagebox.showerror("Hata", f"{asset_type} geçerli bir döviz turu degil!")
        return
    if amount=='0':
        messagebox.showerror("Hata", f"Sifir deger olarak girilemez")
        return
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        iNSERT iNTO transactions (tur, miktar, tarih)
        VALUES (?, ?, datetime('now'))
    ''', (asset_type, amount))
    conn.commit()
    conn.close()
    messagebox.showinfo("Başarili", "Varlik eklendi!")
    varlikyukle()

def varlikkaldir():
    selected_item = assets_listbox.selection()
    if not selected_item:
        messagebox.showwarning("Uyari", "Lutfen kaldirmak istediginiz varligi seçin.")
        return

    item_id = assets_listbox.item(selected_item[0])['values'][0]
    asset_type = assets_listbox.item(selected_item[0])['values'][1]
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE transactions SET kaldirildi=1 WHERE id=?', (item_id,))
        conn.commit()
        messagebox.showinfo("Başarili", "Varlik kaldirildi.")
        varlikyukle()
    except sqlite3.Error as e:
        conn.rollback()
        messagebox.showerror("Hata", "Varlik kaldirilirken bir hata oluştu: " + str(e))
    finally:
        conn.close()

def varlikyukle():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, tur, miktar, tarih FROM transactions WHERE kaldirildi=0')
    rows = cursor.fetchall()
    conn.close()

    for row in assets_listbox.get_children():
        assets_listbox.delete(row)

    for row in rows:
        assets_listbox.insert("", "end", values=row)

def tum_varliklari_yukle():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, tur, miktar, tarih, kaldirildi FROM transactions')
    rows = cursor.fetchall()
    conn.close()

    tum_varliklar_penceresi = tk.Toplevel()
    tum_varliklar_penceresi.title("Tum Varliklar")

    cols = ('iD', 'Varlik Turu', 'Miktar', 'Tarih', 'Kaldirildi')
    tum_varliklar_listbox = ttk.Treeview(tum_varliklar_penceresi, columns=cols, show='headings')

    for col in cols:
        tum_varliklar_listbox.heading(col, text=col)
        tum_varliklar_listbox.column(col, width=100)

    for row in rows:
        tum_varliklar_listbox.insert("", "end", values=row)

    tum_varliklar_listbox.pack(fill="both", expand=True)

def varliklarihesapla():
    total_try = 0
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT tur, miktar FROM transactions WHERE kaldirildi=0')
    rows = cursor.fetchall()
    conn.close()

    doviz_data = dovizcekme(api_key)
    altin_data = altincekme(api_key)

    if doviz_data and altin_data:
        for row in rows:
            asset_type = row[0]
            amount = row[1]

            if asset_type == 'TRY':
                total_try += amount
            else:
                for currency in doviz_data['result']:
                    if currency['code'] == asset_type:
                        total_try += amount * float(currency['selling'])
                        break
                for gold in altin_data['result']:
                    if gold['name'].lower() == asset_type.lower():
                        total_try += amount * float(gold['selling'])
                        break

    return total_try

def varlik_grafigi():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT tarih, tur, miktar FROM transactions WHERE kaldirildi=0')
    rows = cursor.fetchall()
    conn.close()

    tarih_dict = {}
    doviz_data = dovizcekme(api_key)
    altin_data = altincekme(api_key)

    if not doviz_data or not altin_data:
        return

    for row in rows:
        tarih, tur, miktar = row
        if tarih not in tarih_dict:
            tarih_dict[tarih] = 0

        if tur == 'TRY':
            tarih_dict[tarih] += miktar
        else:
            for currency in doviz_data['result']:
                if currency['code'] == tur:
                    tarih_dict[tarih] += miktar * float(currency['selling'])
                    break
            for gold in altin_data['result']:
                if gold['name'].lower() == tur.lower():
                    tarih_dict[tarih] += miktar * float(gold['selling'])
                    break

    tarih_listesi = list(tarih_dict.keys())
    deger_listesi = list(tarih_dict.values())

    fig, ax = plt.subplots()
    ax.plot(tarih_listesi, deger_listesi, marker='o')
    ax.set_xlabel("Tarih")
    ax.set_ylabel("Toplam TRY Degeri")
    ax.set_title("Varliklarin Zaman içindeki Degeri")

    for tick in ax.get_xticklabels():
        tick.set_rotation(45)

    canvas = FigureCanvasTkAgg(fig, master=grafiksekme)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

def kar_zarar_hesapla():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT tur, miktar, tarih FROM transactions WHERE kaldirildi=0')
    rows = cursor.fetchall()
    conn.close()

    doviz_data = dovizcekme(api_key)
    altin_data = altincekme(api_key)

    if not doviz_data or not altin_data:
        return

    current_date = datetime.now()
    kar_zarar_listesi = []

    for row in rows:
        tur, miktar, tarih = row
        tarih = datetime.strptime(tarih, '%Y-%m-%d %H:%M:%S')
        gun_sayisi = (current_date - tarih).days

        if tur == 'TRY':
            continue

        for currency in doviz_data['result']:
            if currency['code'] == tur:
                eski_deger = miktar * float(currency['buying'])
                yeni_deger = miktar * float(currency['selling'])
                kar_zarar_tl = yeni_deger - eski_deger
                kar_zarar_yuzde = (kar_zarar_tl / eski_deger) * 100
                kar_zarar_listesi.append((tur, miktar, tarih.strftime('%Y-%m-%d'), gun_sayisi, kar_zarar_tl, kar_zarar_yuzde))
                break

        for gold in altin_data['result']:
            if gold['name'].lower() == tur.lower():
                eski_deger = miktar * float(gold['buying'])
                yeni_deger = miktar * float(gold['selling'])
                kar_zarar_tl = yeni_deger - eski_deger
                kar_zarar_yuzde = (kar_zarar_tl / eski_deger) * 100
                kar_zarar_listesi.append((tur, miktar, tarih.strftime('%Y-%m-%d'), gun_sayisi, kar_zarar_tl, kar_zarar_yuzde))
                break

    return kar_zarar_listesi

def kar_zarar_goster():
    
    
    kar_zarar_listesi = kar_zarar_hesapla()
    if not kar_zarar_listesi:
        return

    for row in karzarar_listbox.get_children():
        karzarar_listbox.delete(row)

    for item in kar_zarar_listesi:
        karzarar_listbox.insert("", "end", values=item)

def pencereolusturma():
    global assets_listbox, karzarar_listbox, grafiksekme,asset_type_entry,amount_var

    pen = tk.Tk()
    pen.title("Döviz ve Altin Uygulamasi")

    sekme = ttk.Notebook(pen)
    dovizsekme = ttk.Frame(sekme)
    altinsekme = ttk.Frame(sekme)
    varliksekme = ttk.Frame(sekme)
    grafiksekme = ttk.Frame(sekme)
    karzararsekme = ttk.Frame(sekme)

    sekme.add(dovizsekme, text='Döviz')
    sekme.add(altinsekme, text='Altin')
    sekme.add(varliksekme, text='Varliklarim')
    sekme.add(grafiksekme, text='Fiyat Grafikleri')
    sekme.add(karzararsekme, text='Kar Zarar Durumu')

    sekme.pack(expand=1, fill="both")

    doviz_data = dovizcekme(api_key)
    if doviz_data:
        cols = ('Para Birimi', 'Aliş', 'Satiş')
        listbox = ttk.Treeview(dovizsekme, columns=cols, show='headings')

        for col in cols:
            listbox.heading(col, text=col)
            listbox.grid(row=0, column=0, columnspan=2)
            listbox.column(col, width=100)

        for currency in doviz_data['result']:
            listbox.insert("", "end", values=(currency['code'], currency['buying'], currency['selling']))

        listbox.pack(side="left", fill="both", expand=True)

    altin_data = altincekme(api_key)
    if altin_data:
        cols = ('Altin Turu', 'Aliş', 'Satiş')
        listbox = ttk.Treeview(altinsekme, columns=cols, show='headings')

        for col in cols:
            listbox.heading(col, text=col)
            listbox.grid(row=0, column=0, columnspan=2)
            listbox.column(col, width=150)

        for gold in altin_data['result']:
            listbox.insert("", "end", values=(gold['name'], gold['buying'], gold['selling']))

        listbox.pack(side="left", fill="both", expand=True)

    # Varliklarim Sekmesi
    tk.Label(varliksekme, text="Varlik Turu:").grid(row=0, column=0, padx=10, pady=10)
    tk.Label(varliksekme, text="Miktar:").grid(row=1, column=0, padx=10, pady=10)

    asset_type_var = tk.StringVar()
    amount_var = tk.StringVar()
    # Arama fonksiyonu

    asset_type_entry = ttk.Entry(varliksekme, textvariable=asset_type_var)
    amount_entry = ttk.Entry(varliksekme, textvariable=amount_var)

    asset_type_entry.grid(row=0, column=1, padx=10, pady=10)
    amount_entry.grid(row=1, column=1, padx=10, pady=10)

    ttk.Button(varliksekme, text="Ekle", command=lambda: varlikgir(asset_type_var.get(), amount_var.get())).grid(row=2, column=0, padx=10, pady=10)
    ttk.Button(varliksekme, text="Kaldir", command=varlikkaldir).grid(row=2, column=1, padx=10, pady=10)
    ttk.Button(varliksekme, text="Tum Varliklari Göster", command=tum_varliklari_yukle).grid(row=2, column=2, padx=10, pady=10)

    cols = ('iD', 'Varlik Turu', 'Miktar', 'Tarih')
    assets_listbox = ttk.Treeview(varliksekme, columns=cols, show='headings')

    for col in cols:
        assets_listbox.heading(col, text=col)
        assets_listbox.column(col, width=100)

    assets_listbox.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

    varlikyukle()

    # Fiyat Grafikleri Sekmesi
    varlik_grafigi()

    # Kar Zarar Durumu Sekmesi
    karzarar_listbox = ttk.Treeview(karzararsekme, columns=('Tur', 'Miktar', 'Tarih', 'Gun', 'Kar/Zarar (TL)', 'Kar/Zarar (%)'), show='headings')

    for col in ('Tur', 'Miktar', 'Tarih', 'Gun', 'Kar/Zarar (TL)', 'Kar/Zarar (%)'):
        karzarar_listbox.heading(col, text=col)
        karzarar_listbox.column(col, width=100)

    karzarar_listbox.pack(fill='both', expand=True)
    kar_zarar_goster()

    pen.mainloop()

veritabani()
pencereolusturma()
#varliklarihesapla() ve kar_zarar_hesapla() fonksiyonlarında gptden yardım aldım
