# Telegram Test Bot — savollar qo‘shilgan versiya

## Tayyor testlar
- 1–11-sinflar uchun Matematika, Ona tili va Ingliz tili.
- Har bir fan/sinf uchun 18 ta fan savoli + 7 ta IQ savoli.
- Har savolda A, B, C, D variantlari va to‘g‘ri javob bazada saqlangan.
- Test savollari aralashtirib beriladi.
- Yakunda natija va PDF sertifikat yuboriladi.

Eslatma: ushbu boshlang‘ich bazadagi savollar sinflar bo‘yicha alohida murakkablik darajasiga ajratilmagan; bir fan savollari 1–11-sinflarda umumiy qo‘llanadi. Hozircha boshqa fanlar menyuda ko‘rsatilmaydi, chunki ular uchun savollar banki qo‘shilmagan.

## Windows ishga tushirish
1. `.env.example` faylidan nusxa olib `.env` deb nomlang.
2. `.env` ichida `BOT_TOKEN` qatoriga BotFather tokenini, `ADMIN_IDS` qatoriga Telegram ID'ingizni kiriting.
3. PowerShell'da loyiha papkasiga kiring. Agar terminal allaqachon loyiha ichida bo‘lsa, `cd` buyrug‘ini qayta yozmang.
4. Ishga tushiring:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m pip install -r requirements.txt
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" bot.py
```

## O‘quvchi
`/start` → maktab → sinf → F.I.SH. → fan → 25 savol → natija va PDF sertifikat.

## Admin
- `/admin` — admin panel
- `/addquestion` — qo‘shimcha savol kiritish
- `/stats` — savollar statistikasi
- `/cancel` — kiritishni bekor qilish

Admin qo‘shadigan savollar uchun har bir karta 18 ta `fan` va 7 ta `iq` savolga yetganda test tanlanadi.
