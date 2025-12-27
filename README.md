# BlazeFace Raw ONNX (NMS’siz)
### Unity Sentis ve Meta Quest 3S için model hazırlık rehberi

Bu repository’nin amacı, Blaze / BlazeFace tabanlı yüz tespit ONNX modelini Unity Sentis ile stabil biçimde çalıştırabilmek için modeli NonMaxSuppression (NMS) katmanından önce sonlandırılmış “raw” hale getirmektir.

BlazeFace modelleri ONNX graph’ının sonunda genellikle NonMaxSuppression → Gather → Squeeze zinciri içerir. Bu zincir, Unity Sentis tarafında tensor index uyuşmazlıkları ve runtime hatalarına neden olabilmektedir. Bu repo, NMS işlemini Unity tarafına taşıyarak bu problemi kalıcı biçimde çözer.

---

## Problem Tanımı

BlazeFace ONNX graph’ı tipik olarak şu adımları içerir:

- Bounding box regression (yüz adaylarının koordinatları)
- Confidence / score hesaplama
- ONNX içinde çalışan NonMaxSuppression
- NMS sonrası Gather ve Squeeze işlemleri

Unity Sentis:

- Bazı ONNX NonMaxSuppression konfigürasyonlarını desteklemez
- NMS sonrası tensor index’lerinin beklenenden farklı gelmesi durumunda
  runtime sırasında hata üretir
- Özellikle mobil ve XR cihazlarda bu durum daha sık görülür

Bu nedenle modelin, NMS uygulanmış son çıktılarıyla değil, ham (raw) tensörleriyle Unity’ye verilmesi gerekir.

---

<img width="716" height="655" alt="Ekran Resmi 2025-12-27 10 26 23" src="https://github.com/user-attachments/assets/e4e8e6f9-55eb-4f97-b460-2efda8cf09d4" />

### Blaze_Onnx Tam Nöral Ağı: [blaze.onnx.pdf](https://github.com/user-attachments/files/24353516/blaze.onnx.pdf)


## Çözüm Yaklaşımı

Bu repository modeli yeniden eğitmez veya ağırlıklarını değiştirmez.

Yapılan işlem yalnızca ONNX graph’ının output noktasını değiştirmektir.

Yeni akış:

1. BlazeFace modeli çalışır
2. NonMaxSuppression katmanından hemen önceki tensörler dışarı verilir
3. ONNX graph burada sonlandırılır
4. Unity Sentis yalnızca ham tensörleri üretir
5. NonMaxSuppression ve threshold işlemleri Unity C# tarafında yapılır

Bu yaklaşım Unity Sentis uyumsuzluklarını ortadan kaldırır ve Quest 3S gibi cihazlarda stabil sonuç alınmasını sağlar.

---

## Üretilen Model: blaze_raw.onnx

Bu repo sonunda elde edilen blaze_raw.onnx dosyası:

- NonMaxSuppression içermez
- Modelin son katmanı ham tensörlerdir
- Genellikle iki output üretir:
  - Bounding box koordinatları (boxes / locations)
  - Confidence skorları (scores / classification)

Tipik tensör boyutları model varyantına göre değişebilir ancak çoğunlukla:

- Boxes: 1 × 896 × 4
- Scores: 1 × 896 × 1 veya 1 × 1 × 896

---

## 1 — Blaze ONNX’i “Raw” Hale Getirme

### Netron ile doğru tensörleri belirleme

Netron, ONNX modelini görselleştirmek için kullanılır.

Bu aşamada yapılması gerekenler:

- BlazeFace ONNX dosyasını Netron’da aç
- Graph içinde NonMaxSuppression node’unu bul
- Bu node’a giren input tensörleri incele
- Aşağıdaki iki tensörün isimlerini birebir not al:
  - Bounding box (regression) tensörü
  - Confidence / score tensörü

Bu isimler modelden modele değişebilir. Örnek olarak:

- raw_boxes, raw_scores
- loc, conf
- Identity_3:0 gibi otomatik isimler

Bu adım kritiktir. Tensör isimleri yanlış alınırsa raw model doğru şekilde oluşturulamaz.

---

### ONNX output’larının yeniden tanımlanması

Bu aşamada modelin mevcut output tanımları kaldırılır ve yerine:

- Bounding box tensörü
- Confidence tensörü

output olarak eklenir.

Bu işlem:

- Model ağırlıklarına dokunmaz
- Hesaplama grafiğini değiştirmez
- Sadece graph’ın nerede sonlandığını yeniden tanımlar

Sonuç olarak:

- NonMaxSuppression node’u graph içinde kalsa bile çalıştırılmaz
- Unity Sentis yalnızca ham tensörleri alır

---

## Unity Tarafında Beklenen Kullanım

Bu repo yalnızca modelin raw hale getirilmesini kapsar.

Unity tarafında tipik kullanım akışı:

1. blaze_raw.onnx Sentis ile yüklenir
2. Inference çalıştırılır
3. Aşağıdaki çıktılar alınır:
   - Bounding box tensörleri
   - Confidence skorları
4. C# tarafında:
   - Confidence threshold uygulanır
   - IoU hesaplanır
   - NonMaxSuppression çalıştırılır
   - Maksimum yüz sayısı sınırlandırılır
5. Sonuçlar UI overlay ile çizilir

Bu yaklaşım mobil XR cihazlarda daha kontrollü ve debug edilebilir bir pipeline sağlar.

---

## Neden NMS Unity Tarafında Yapılıyor?

- Sentis ONNX NMS implementasyonuna bağımlılık kalkar
- Runtime’da threshold değerleri dinamik olarak değiştirilebilir
- Multi-face senaryoları daha rahat yönetilir
- Quest 3S gibi cihazlarda deterministik sonuç elde edilir

Özetle:
Model hesaplasın, karar mantığı Unity tarafında olsun.

---

## Teknik Notlar

- Bu repo bir hack değildir
- MediaPipe ve Blaze tabanlı birçok mobil pipeline NMS’yi runtime tarafına taşır
- Aynı yaklaşım YOLO ve SSD gibi modellerde de yaygın olarak kullanılır

---

## Lisans ve Sorumluluk

Bu repo yalnızca ONNX graph output düzenlemesi yapar.  
Modelin lisansı ve kullanım koşulları orijinal BlazeFace dağıtımına aittir.
