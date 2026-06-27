Proje Adı
CYK Algoritması ile Söz Dizimi Analizi

Ders ve Proje No
Biçimsel Diller ve Otomata
Proje No 5: CYK Algoritması ile Söz Dizimi Analizi

Kullanılan Dil ve Kütüphane
Bu proje Python 3 ile yazılmıştır. Arayüz için Python'un standart kütüphanesinde bulunan Tkinter kullanılmıştır. Harici kütüphane kurulmasına gerek yoktur.

Program Nasıl Çalıştırılır?
1. main.py, gramer.txt, ornek_kabul.txt ve ornek_red.txt dosyaları aynı klasörde bulunmalıdır.
2. main.py dosyası Python 3 ile çalıştırılır.
3. Açılan arayüzde "Gramer Dosyası Seç" butonu ile gramer.txt dosyası seçilir.
4. Analiz edilecek kelime yazılır.
5. "Analiz Et" butonuna basılarak sonuç ve CYK tablosu görülür.

Gramer Dosyası Formatı
Bu projede CNF biçiminde verilen bir gramer için girilen kelimenin CYK algoritması ile kabul edilip edilmediği kontrol edilmektedir. Gramer kuralları kodun içine yazılmamış, Notepad ile düzenlenebilen gramer.txt dosyasından okunmuştur.

Her satırda bir değişkene ait üretim kuralları bulunur. Sol taraf ve sağ taraf "->" ile ayrılır. Aynı değişken için birden fazla üretim varsa "|" işareti kullanılır.

Örnek format:
S -> AB | BC
A -> BA | a
B -> CC | b
C -> AB | a

CNF için kabul edilen kural biçimleri:
A -> BC
A -> a
A -> 0

Sol taraf tek büyük harf olmalıdır. Sağ taraf ya iki büyük değişken ya da tek karakter terminal olmalıdır.

Örnek Kabul Kelimesi
baaba

Örnek Red Kelimesi
aaaa

CYK Algoritmasının Kısa Mantığı
Program önce gramer dosyasını okur ve kuralların Chomsky Normal Form'a uygun olup olmadığını kontrol eder. Daha sonra kullanıcının girdiği kelime için CYK tablosu oluşturulur.

İlk olarak kelimedeki tek karakterleri üreten değişkenler tablonun alt satırına yazılır. Sonra daha uzun alt kelimeler için olası bölünmeler denenir. Sol ve sağ parçaları üreten değişkenler birleştirilerek gramerde karşılığı olup olmadığına bakılır. En üst hücrede başlangıç sembolü S varsa kelime kabul edilir, yoksa reddedilir.

Not
Başlangıç sembolü S olarak alınmıştır.
