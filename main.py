# -*- coding: utf-8 -*-
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class GramerHatasi(Exception):
    """Gramer dosyası okunurken oluşan anlaşılır hatalar için kullanılır."""


def metin_dosyasini_oku(dosya_yolu):
    try:
        with open(dosya_yolu, "r", encoding="utf-8-sig") as dosya:
            return dosya.readlines()
    except UnicodeDecodeError:
        with open(dosya_yolu, "r", encoding="cp1254") as dosya:
            return dosya.readlines()


def gramer_dosyasini_oku(dosya_yolu):
    # Gramer dosyasındaki kuralları okur
    gramer = {}

    try:
        satirlar = metin_dosyasini_oku(dosya_yolu)
    except FileNotFoundError:
        raise GramerHatasi("Dosya bulunamadı.")

    for satir_no, ham_satir in enumerate(satirlar, start=1):
        satir = ham_satir.strip()

        if not satir or satir.startswith("#"):
            continue

        if "->" not in satir:
            raise GramerHatasi(f"{satir_no}. satırda '->' işareti bulunamadı: {satir}")

        sol_taraf, sag_taraf = satir.split("->", 1)
        sol_taraf = sol_taraf.strip()
        sag_taraf = sag_taraf.strip()

        if not sol_taraf or not sag_taraf:
            raise GramerHatasi(f"{satir_no}. satırda eksik kural var: {satir}")

        uretimler = [parca.strip() for parca in sag_taraf.split("|")]
        if any(uretim == "" for uretim in uretimler):
            raise GramerHatasi(f"{satir_no}. satırda boş üretim kuralı var: {satir}")

        if sol_taraf not in gramer:
            gramer[sol_taraf] = []
        gramer[sol_taraf].extend(uretimler)

    if not gramer:
        raise GramerHatasi("Gramer dosyasında okunabilir kural bulunamadı.")

    return gramer


def degisken_mi(sembol):
    return len(sembol) == 1 and sembol.isalpha() and sembol.isupper()


def terminal_mi(sembol):
    return len(sembol) == 1 and not sembol.isupper()


def cnf_kontrol_et(gramer):
    # CNF biçimine uygunluk kontrol edilir
    for sol_taraf, uretimler in gramer.items():
        if not degisken_mi(sol_taraf):
            ornek_kural = f"{sol_taraf} -> {' | '.join(uretimler)}"
            return (
                False,
                f"CNF Hatası: {ornek_kural} kuralı uygun değildir. "
                "Sol taraf tek büyük harf olmalıdır.",
            )

        for uretim in uretimler:
            gecerli_degisken_cifti = len(uretim) == 2 and all(
                degisken_mi(sembol) for sembol in uretim
            )
            gecerli_terminal = terminal_mi(uretim)

            if not (gecerli_degisken_cifti or gecerli_terminal):
                return (
                    False,
                    f"CNF Hatası: {sol_taraf} -> {uretim} kuralı uygun değildir. "
                    "Sağ taraf ya iki değişken ya da tek terminal olmalıdır.",
                )

    return True, "CNF Kontrolü: Gramer Chomsky Normal Form'a uygundur."


def kural_haritalarini_olustur(gramer):
    terminal_kurallari = {}
    ikili_kurallar = {}

    for sol_taraf, uretimler in gramer.items():
        for uretim in uretimler:
            if terminal_mi(uretim):
                terminal_kurallari.setdefault(uretim, set()).add(sol_taraf)
            else:
                ikili_kurallar.setdefault(uretim, set()).add(sol_taraf)

    return terminal_kurallari, ikili_kurallar


def cyk_analizi_yap(gramer, kelime, baslangic_sembolu="S"):
    terminal_kurallari, ikili_kurallar = kural_haritalarini_olustur(gramer)
    uzunluk = len(kelime)
    tablo = [[set() for _ in range(uzunluk)] for _ in range(uzunluk)]

    # İlk satır terminal kurallarıyla doldurulur
    for sira, karakter in enumerate(kelime):
        tablo[0][sira].update(terminal_kurallari.get(karakter, set()))

    # Daha uzun parçalar için olası bölünmeler denenir
    for parca_uzunlugu in range(2, uzunluk + 1):
        for baslangic in range(uzunluk - parca_uzunlugu + 1):
            for bolme in range(1, parca_uzunlugu):
                sol_hucre = tablo[bolme - 1][baslangic]
                sag_hucre = tablo[parca_uzunlugu - bolme - 1][baslangic + bolme]

                for sol_degisken in sol_hucre:
                    for sag_degisken in sag_hucre:
                        degisken_cifti = sol_degisken + sag_degisken
                        tablo[parca_uzunlugu - 1][baslangic].update(
                            ikili_kurallar.get(degisken_cifti, set())
                        )

    # En üst hücrede S varsa kelime kabul edilir
    kabul_edildi = baslangic_sembolu in tablo[uzunluk - 1][0] if uzunluk > 0 else False
    return kabul_edildi, tablo


def hucreyi_yazdir(hucre):
    if not hucre:
        return "∅"
    return ",".join(sorted(hucre))


def grameri_metne_cevir(gramer):
    metin_satirlari = []
    for sol_taraf, uretimler in gramer.items():
        metin_satirlari.append(f"{sol_taraf} -> {' | '.join(uretimler)}")
    return "\n".join(metin_satirlari)


class CYKUygulamasi:
    def __init__(self, kok):
        self.kok = kok
        self.gramer = None
        self.gramer_yolu = ""
        self.cnf_uygun = False
        self.arka_plan_rengi = "#f5f7fb"
        self.panel_rengi = "#ffffff"
        self.metin_rengi = "#1f2937"
        self.soluk_renk = "#64748b"

        self.kok.title("CYK Algoritması ile Söz Dizimi Analizi")
        self.kok.geometry("1200x780")
        self.kok.minsize(1000, 650)
        self.kok.configure(bg=self.arka_plan_rengi)

        self.stil_ayarla()
        self.arayuzu_olustur()

    def stil_ayarla(self):
        stil = ttk.Style()
        try:
            stil.theme_use("clam")
        except tk.TclError:
            pass

        stil.configure(".", font=("Segoe UI", 10))
        stil.configure("Main.TFrame", background=self.arka_plan_rengi)
        stil.configure("Panel.TFrame", background=self.panel_rengi)
        stil.configure("TLabel", background=self.arka_plan_rengi, foreground=self.metin_rengi)
        stil.configure("Muted.TLabel", background=self.arka_plan_rengi, foreground=self.soluk_renk)
        stil.configure("Panel.TLabel", background=self.panel_rengi, foreground=self.metin_rengi)
        stil.configure("Info.TLabel", background=self.panel_rengi, foreground=self.soluk_renk)
        stil.configure("TButton", padding=(8, 4), font=("Segoe UI", 10))
        stil.configure("Primary.TButton", padding=(10, 5), font=("Segoe UI", 10, "bold"))
        stil.configure("TEntry", padding=4)
        stil.configure("TLabelframe", background=self.arka_plan_rengi)
        stil.configure(
            "TLabelframe.Label",
            background=self.arka_plan_rengi,
            foreground="#0f172a",
            font=("Segoe UI", 10, "bold"),
        )

    def arayuzu_olustur(self):
        ana_cerceve = ttk.Frame(self.kok, padding=(10, 6, 10, 4), style="Main.TFrame")
        ana_cerceve.pack(fill="both", expand=True)

        baslik_cercevesi = ttk.Frame(ana_cerceve, style="Main.TFrame")
        baslik_cercevesi.pack(fill="x", pady=(0, 4))

        baslik_etiketi = ttk.Label(
            baslik_cercevesi,
            text="CYK Algoritması ile Söz Dizimi Analizi",
            font=("Segoe UI", 18, "bold"),
        )
        baslik_etiketi.pack(anchor="center")

        alt_aciklama_etiketi = ttk.Label(
            baslik_cercevesi,
            text="CNF formatındaki grameri dosyadan okuyarak kelimenin kabul/red durumunu CYK tablosu ile gösterir.",
            style="Muted.TLabel",
            font=("Segoe UI", 10),
        )
        alt_aciklama_etiketi.pack(anchor="center", pady=(1, 0))

        gramer_cercevesi = ttk.LabelFrame(ana_cerceve, text="Gramer Dosyası", padding=(6, 4))
        gramer_cercevesi.pack(fill="x", pady=(0, 4))

        buton_cercevesi = ttk.Frame(gramer_cercevesi)
        buton_cercevesi.pack(fill="x", pady=(0, 4))

        sec_butonu = ttk.Button(
            buton_cercevesi,
            text="Gramer Dosyası Seç",
            command=self.gramer_dosyasi_sec,
            style="Primary.TButton",
        )
        sec_butonu.pack(side="left")

        ornek_butonu = ttk.Button(
            buton_cercevesi,
            text="Örnek Grameri Yükle",
            command=self.ornek_grameri_yukle,
        )
        ornek_butonu.pack(side="left", padx=6)

        self.dosya_etiketi = ttk.Label(
            buton_cercevesi,
            text="Seçilen dosya: Yok",
            style="Muted.TLabel",
        )
        self.dosya_etiketi.pack(side="left", padx=8)

        metin_cercevesi = ttk.Frame(gramer_cercevesi)
        metin_cercevesi.pack(fill="x", pady=(0, 4))

        self.gramer_metni = tk.Text(
            metin_cercevesi,
            height=4,
            wrap="word",
            font=("Consolas", 10),
            bg="#ffffff",
            fg="#111827",
            relief="solid",
            borderwidth=1,
            padx=6,
            pady=4,
        )
        self.gramer_metni.pack(side="left", fill="x", expand=True)
        self.gramer_metni.config(state="disabled")

        gramer_kaydirma = ttk.Scrollbar(metin_cercevesi, command=self.gramer_metni.yview)
        gramer_kaydirma.pack(side="right", fill="y")
        self.gramer_metni.config(yscrollcommand=gramer_kaydirma.set)

        self.cnf_etiketi = tk.Label(
            gramer_cercevesi,
            text="CNF Kontrolü: Henüz gramer yüklenmedi.",
            anchor="w",
            padx=8,
            pady=5,
            bg="#eef2f7",
            fg="#334155",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 10, "bold"),
        )
        self.cnf_etiketi.pack(fill="x")

        giris_cercevesi = ttk.LabelFrame(ana_cerceve, text="Kelime Analizi", padding=(6, 4))
        giris_cercevesi.pack(fill="x", pady=4)

        kelime_cercevesi = ttk.Frame(giris_cercevesi)
        kelime_cercevesi.pack(fill="x", pady=(0, 4))

        ttk.Label(kelime_cercevesi, text="Analiz edilecek kelime:").pack(side="left")
        self.kelime_girdisi = ttk.Entry(kelime_cercevesi, width=40)
        self.kelime_girdisi.pack(side="left", padx=8)
        self.kelime_girdisi.bind("<Return>", lambda olay: self.kelimeyi_analiz_et())

        analiz_butonu = ttk.Button(
            kelime_cercevesi,
            text="Analiz Et",
            command=self.kelimeyi_analiz_et,
            style="Primary.TButton",
        )
        analiz_butonu.pack(side="left", padx=4)

        temizle_butonu = ttk.Button(kelime_cercevesi, text="Temizle", command=self.analizi_temizle)
        temizle_butonu.pack(side="left", padx=4)

        self.baslangic_sembolu_etiketi = ttk.Label(
            giris_cercevesi,
            text="Başlangıç sembolü varsayılan olarak S kabul edilmiştir.",
            style="Muted.TLabel",
            font=("Segoe UI", 9),
            anchor="w",
        )
        self.baslangic_sembolu_etiketi.pack(fill="x", pady=(0, 4))

        self.sonuc_etiketi = tk.Label(
            giris_cercevesi,
            text="Analiz Sonucu: Henüz analiz yapılmadı",
            font=("Segoe UI", 12, "bold"),
            anchor="w",
            padx=10,
            pady=6,
            bg="#eef2f7",
            fg="#334155",
            relief="solid",
            borderwidth=1,
        )
        self.sonuc_etiketi.pack(fill="x", pady=(0, 4))

        self.aciklama_etiketi = ttk.Label(
            giris_cercevesi,
            text="",
            style="Muted.TLabel",
            anchor="w",
        )
        self.aciklama_etiketi.pack(fill="x")

        tablo_cercevesi = ttk.LabelFrame(ana_cerceve, text="CYK Tablosu", padding=(6, 4))
        tablo_cercevesi.pack(fill="both", expand=True, pady=(0, 4))

        tablo_alani = ttk.Frame(tablo_cercevesi)
        tablo_alani.pack(fill="both", expand=True)

        self.tablo_tuvali = tk.Canvas(
            tablo_alani,
            bg="#ffffff",
            height=280,
            highlightthickness=1,
            highlightbackground="#cbd5e1",
        )
        self.tablo_tuvali.pack(side="left", fill="both", expand=True)

        dikey_tablo_kaydirma = ttk.Scrollbar(
            tablo_alani, orient="vertical", command=self.tablo_tuvali.yview
        )
        dikey_tablo_kaydirma.pack(side="right", fill="y")

        yatay_tablo_kaydirma = ttk.Scrollbar(
            tablo_cercevesi, orient="horizontal", command=self.tablo_tuvali.xview
        )
        yatay_tablo_kaydirma.pack(fill="x", pady=(2, 0))

        self.tablo_tuvali.configure(
            yscrollcommand=dikey_tablo_kaydirma.set,
            xscrollcommand=yatay_tablo_kaydirma.set,
        )

        self.tablo_ici = tk.Frame(self.tablo_tuvali, bg="#ffffff")
        self.tablo_penceresi = self.tablo_tuvali.create_window(
            (0, 0),
            window=self.tablo_ici,
            anchor="nw",
        )
        self.tablo_ici.bind("<Configure>", self.tablo_kaydirma_alanini_guncelle)

        adim_cercevesi = ttk.LabelFrame(ana_cerceve, text="Adım Açıklamaları", padding=(6, 4))
        adim_cercevesi.pack(fill="x", pady=(0, 4))

        self.adim_metni = tk.Text(
            adim_cercevesi,
            height=3,
            wrap="word",
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#111827",
            relief="solid",
            borderwidth=1,
            padx=6,
            pady=4,
        )
        self.adim_metni.pack(fill="x")
        self.adim_metni.config(state="disabled")

        alt_bilgi_etiketi = ttk.Label(
            ana_cerceve,
            text="Biçimsel Diller ve Otomata - Proje No 5",
            style="Muted.TLabel",
            font=("Segoe UI", 9),
        )
        alt_bilgi_etiketi.pack(anchor="center", pady=(0, 2))

        self.ilk_mesajlari_goster()

    def tablo_kaydirma_alanini_guncelle(self, olay=None):
        self.tablo_tuvali.configure(scrollregion=self.tablo_tuvali.bbox("all"))

    def metin_kutusunu_ayarla(self, arac, metin, renk="#111827"):
        arac.config(state="normal", fg=renk)
        arac.delete("1.0", tk.END)
        arac.insert(tk.END, metin)
        arac.config(state="disabled")

    def ilk_mesajlari_goster(self):
        gramer_mesaji = (
            "Henüz gramer yüklenmedi.\n"
            "Lütfen 'Gramer Dosyası Seç' butonu ile gramer.txt dosyasını seçin."
        )
        self.metin_kutusunu_ayarla(self.gramer_metni, gramer_mesaji, self.soluk_renk)
        self.sonuc_alanini_sifirla()
        self.bos_tablo_mesaji_goster()
        self.bos_adim_mesaji_goster()

    def sonuc_alanini_sifirla(self):
        self.sonuc_etiketi.config(
            text="Analiz Sonucu: Henüz analiz yapılmadı",
            bg="#eef2f7",
            fg="#334155",
        )
        self.aciklama_etiketi.config(text="")

    def bos_tablo_mesaji_goster(self):
        for arac in self.tablo_ici.winfo_children():
            arac.destroy()

        mesaj = tk.Label(
            self.tablo_ici,
            text="Analiz yapıldığında CYK tablosu burada gösterilecektir.",
            bg="#ffffff",
            fg=self.soluk_renk,
            font=("Segoe UI", 10),
            padx=24,
            pady=22,
        )
        mesaj.grid(row=0, column=0, sticky="w")
        self.tablo_kaydirma_alanini_guncelle()

    def bos_adim_mesaji_goster(self):
        self.metin_kutusunu_ayarla(
            self.adim_metni,
            "Analiz yapıldığında CYK algoritmasının adımları burada gösterilecektir.",
            self.soluk_renk,
        )

    def gramer_dosyasi_sec(self):
        dosya_yolu = filedialog.askopenfilename(
            title="Gramer Dosyası Seç",
            filetypes=[("Metin Dosyaları", "*.txt"), ("Tüm Dosyalar", "*.*")],
        )
        if dosya_yolu:
            self.grameri_yukle(dosya_yolu)

    def ornek_grameri_yukle(self):
        ornek_yol = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gramer.txt")
        self.grameri_yukle(ornek_yol)

    def grameri_yukle(self, dosya_yolu):
        try:
            gramer = gramer_dosyasini_oku(dosya_yolu)
        except GramerHatasi as hata:
            messagebox.showerror("Gramer Hatası", str(hata))
            return

        self.gramer = gramer
        self.gramer_yolu = dosya_yolu
        self.dosya_etiketi.config(text=f"Seçilen dosya: {os.path.basename(dosya_yolu)}")
        self.grameri_goster(gramer)

        self.cnf_uygun, cnf_mesaji = cnf_kontrol_et(gramer)
        if self.cnf_uygun:
            self.cnf_etiketi.config(text=cnf_mesaji, bg="#dff4e4", fg="#166534")
        else:
            self.cnf_etiketi.config(text=cnf_mesaji, bg="#fde2e2", fg="#991b1b")

        self.analizi_temizle(kelimeyi_koru=True)

    def grameri_goster(self, gramer):
        self.metin_kutusunu_ayarla(self.gramer_metni, grameri_metne_cevir(gramer))

    def kelimeyi_analiz_et(self):
        if self.gramer is None:
            messagebox.showwarning("Uyarı", "Lütfen önce bir gramer dosyası seçin.")
            return

        self.cnf_uygun, cnf_mesaji = cnf_kontrol_et(self.gramer)
        if not self.cnf_uygun:
            self.cnf_etiketi.config(text=cnf_mesaji, bg="#fde2e2", fg="#991b1b")
            messagebox.showerror("CNF Hatası", cnf_mesaji)
            return

        kelime = self.kelime_girdisi.get().strip()
        if not kelime:
            messagebox.showwarning("Uyarı", "Lütfen analiz edilecek kelimeyi girin.")
            return

        self.bilinmeyen_terminal_uyarisi(kelime)

        kabul_edildi, tablo = cyk_analizi_yap(self.gramer, kelime)
        self.cyk_tablosunu_goster(tablo, kelime)
        self.adimlari_goster()

        if kabul_edildi:
            self.sonuc_etiketi.config(
                text="Analiz Sonucu: KABUL EDİLDİ",
                bg="#dff4e4",
                fg="#166534",
            )
            self.aciklama_etiketi.config(
                text="Başlangıç sembolü S, CYK tablosunun en üst hücresinde bulundu."
            )
        else:
            self.sonuc_etiketi.config(
                text="Analiz Sonucu: REDDEDİLDİ",
                bg="#fde2e2",
                fg="#991b1b",
            )
            self.aciklama_etiketi.config(
                text="Başlangıç sembolü S, CYK tablosunun en üst hücresinde bulunamadı."
            )

    def bilinmeyen_terminal_uyarisi(self, kelime):
        terminaller = {
            uretim
            for uretimler in self.gramer.values()
            for uretim in uretimler
            if terminal_mi(uretim)
        }
        bilinmeyen_karakterler = sorted(
            {karakter for karakter in kelime if karakter not in terminaller}
        )

        if bilinmeyen_karakterler:
            karakterler = ", ".join(bilinmeyen_karakterler)
            messagebox.showwarning(
                "Terminal Uyarısı",
                "Kelimedeki şu karakterler gramer terminallerinde yok: "
                f"{karakterler}\nAnaliz devam edecek; bu karakterleri üreten kural yoksa sonuç red olur.",
            )

    def cyk_tablosunu_goster(self, tablo, kelime):
        for arac in self.tablo_ici.winfo_children():
            arac.destroy()

        uzunluk = len(kelime)
        if uzunluk == 0:
            self.bos_tablo_mesaji_goster()
            return

        for parca_uzunlugu in range(uzunluk, 0, -1):
            satir = uzunluk - parca_uzunlugu
            for baslangic in range(uzunluk - parca_uzunlugu + 1):
                alt_kelime = kelime[baslangic : baslangic + parca_uzunlugu]
                hucre_metni = f"{alt_kelime}\n{hucreyi_yazdir(tablo[parca_uzunlugu - 1][baslangic])}"

                if parca_uzunlugu == uzunluk:
                    arka_plan = "#e7f0ff"
                elif parca_uzunlugu == 1:
                    arka_plan = "#f0f7ec"
                else:
                    arka_plan = "#f8fafc"

                etiket = tk.Label(
                    self.tablo_ici,
                    text=hucre_metni,
                    width=14,
                    height=3,
                    relief="solid",
                    borderwidth=1,
                    bg=arka_plan,
                    fg="#111827",
                    font=("Consolas", 10),
                    justify="center",
                )
                etiket.grid(row=satir, column=baslangic, padx=3, pady=3, sticky="nsew")

    def adimlari_goster(self):
        adimlar = (
            "1. adım: Kelimedeki tek karakterler için terminal kuralları kontrol edildi.\n"
            "2. adım: İki ve daha uzun alt diziler için parçalama işlemleri yapıldı.\n"
            "3. adım: Her parçanın hangi değişkenler tarafından üretilebildiği CYK tablosuna yazıldı.\n"
            "4. adım: En üst hücrede başlangıç sembolü S aranarak kabul/red kararı verildi."
        )
        self.metin_kutusunu_ayarla(self.adim_metni, adimlar)

    def analizi_temizle(self, kelimeyi_koru=False):
        if not kelimeyi_koru:
            self.kelime_girdisi.delete(0, tk.END)

        self.sonuc_alanini_sifirla()
        self.bos_tablo_mesaji_goster()
        self.bos_adim_mesaji_goster()


if __name__ == "__main__":
    kok = tk.Tk()
    uygulama = CYKUygulamasi(kok)
    kok.mainloop()
