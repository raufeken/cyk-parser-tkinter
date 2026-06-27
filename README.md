# CYK Parser — Söz Dizimi Analizörü

> CNF biçimindeki gramerler için CYK algoritması ile söz dizimi analizi yapan Python/Tkinter tabanlı masaüstü uygulaması.

Bu proje, **Biçimsel Diller ve Otomata** dersi kapsamında geliştirilmiştir. Kullanıcıdan alınan bir kelimenin, Chomsky Normal Form (CNF) biçimindeki bir gramer tarafından üretilip üretilemediği CYK algoritması kullanılarak analiz edilir.

---

## Proje Hakkında

Bu uygulama, dışarıdan yüklenen bir gramer dosyasını okuyarak girilen kelimenin kabul veya red durumunu belirler. Gramer kuralları kod içine sabit yazılmamıştır; kullanıcı tarafından düzenlenebilen `gramer.txt` dosyasından okunur.

Program analiz öncesinde gramerin CNF formatına uygun olup olmadığını kontrol eder. Analiz sonucunda kabul/red bilgisi, kısa açıklama ve CYK tablosu arayüz üzerinde gösterilir.

---

## Kullanılan Teknolojiler

| Teknoloji      | Açıklama                             |
| -------------- | ------------------------------------ |
| Python 3       | Ana programlama dili                 |
| Tkinter        | Masaüstü arayüz geliştirme           |
| Tkinter Canvas | CYK tablosunu görsel olarak gösterme |
| TXT Dosyaları  | Gramer ve örnek kelime girişi        |

> Harici kütüphane kurulumu gerekmez.

---

## Özellikler

* Gramer kurallarını `.txt` dosyasından okuma
* CNF uygunluk kontrolü yapma
* CYK algoritması ile kelime analizi
* Kabul / red sonucunu gösterme
* CYK tablosunu arayüzde görselleştirme
* Hatalı gramer formatlarında kullanıcıya uyarı verme
* Kabul ve red örnek dosyaları ile test edebilme

---

## Nasıl Çalıştırılır?

Bilgisayarınızda Python 3 kurulu olmalıdır.

Aşağıdaki dosyaların aynı klasörde olduğundan emin olun:

```text
main.py
gramer.txt
ornek_kabul.txt
ornek_red.txt
```

Programı çalıştırmak için terminalde şu komutu kullanın:

```bash
python main.py
```

Ardından:

1. **Gramer Dosyası Seç** butonuna basın.
2. `gramer.txt` dosyasını seçin.
3. Analiz edilecek kelimeyi girin.
4. **Analiz Et** butonuna basın.
5. CYK tablosunu ve kabul/red sonucunu görüntüleyin.

---

## Gramer Dosyası Formatı

Gramer kuralları aşağıdaki formatta yazılmalıdır:

```text
S -> AB | BC
A -> BA | a
B -> CC | b
C -> AB | a
```

CNF için kabul edilen kural biçimleri:

```text
A -> BC
A -> a
```

Kurallar:

* Sol taraf tek büyük harf olmalıdır.
* Sağ taraf ya iki büyük değişken ya da tek terminal karakter olmalıdır.
* Başlangıç sembolü `S` olarak kabul edilmiştir.

---

## Örnek Testler

| Kelime  | Sonuç |
| ------- | ----- |
| `baaba` | Kabul |
| `aaaa`  | Red   |

---

## CYK Algoritmasının Mantığı

1. Gramer dosyası okunur ve CNF uygunluğu kontrol edilir.
2. Kelimedeki tek karakterleri üreten değişkenler tablonun alt satırına yazılır.
3. Daha uzun alt kelimeler için tüm olası bölünme noktaları denenir.
4. Sol ve sağ parçaları üreten değişkenler birleştirilerek gramerde karşılığı aranır.
5. En üst hücrede başlangıç sembolü `S` varsa kelime kabul edilir, yoksa reddedilir.

---

## Proje Yapısı

```text
cyk-parser-tkinter/
├── main.py
├── gramer.txt
├── ornek_kabul.txt
├── ornek_red.txt
└── README.md
```

---

## Sonuç

Bu proje, CYK algoritmasının dinamik programlama mantığını ve CNF gramer yapısını uygulamalı olarak göstermek amacıyla geliştirilmiştir. Tkinter arayüzü sayesinde kullanıcı gramer dosyası seçebilir, kelime analizi yapabilir ve oluşan CYK tablosunu görsel olarak inceleyebilir.
