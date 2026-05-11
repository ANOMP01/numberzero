# numberzero

Tool untuk memposting tweet yang sama dari banyak akun X sekaligus.

---

## Cara Pakai

```
python sessions.py                                    # login & simpan session
python toolsx.py --session -t "Event!" -m poster.jpg  # posting
```

---

## 1. Install

```
git clone https://github.com/ANOMP01/numberzero.git
cd numberzero
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
```

---

## 2. Edit emails.txt

File emails.txt sudah ada di folder project. Buka dan edit isinya:

```
password: cloudin123

senoie001@dineram.com
senoie002@dineram.com
senoie003@dineram.com
senoie004@dineram.com
senoie005@dineram.com
```

Baris pertama = password. Sisanya = email (satu per baris).

---

## 3. Login & simpan session

```
python sessions.py
```

---

## 4. Posting

```
python toolsx.py --session -t "Event Sabtu 19.00!" -m media/images/poster.jpg
```

---

## 5. Taruh gambar/video

```
media/images/   ← .jpg .png .webp
media/videos/   ← .mp4 .mov .gif
```
