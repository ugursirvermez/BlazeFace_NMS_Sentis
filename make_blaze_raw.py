import onnx
from onnx import helper, shape_inference

IN_PATH  = "blaze.onnx"
OUT_PATH = "blaze_raw.onnx"

# Netron'dan bulduğun İSİMLERİ buraya yaz:
BOXES_NAME  = "finalBoxesCoords"
SCORES_NAME = "finalScores_T"

m = onnx.load(IN_PATH)
g = m.graph

# Mevcut outputları temizle
del g.output[:]

# Graph'taki value_info / initializer / input / output listelerinde tensor arayalım
all_known = {vi.name for vi in g.value_info}
all_known |= {i.name for i in g.input}
all_known |= {o.name for o in g.output}
all_known |= {init.name for init in g.initializer}

missing = [n for n in [BOXES_NAME, SCORES_NAME] if n not in all_known]
if missing:
    print("UYARI: Bu tensor isimleri graph'ta doğrudan görünmedi:", missing)
    print("Netron'da NMS input isimlerini birebir kopyaladığından emin ol.")
    # Yine de denemeye devam edeceğiz; bazı modeller value_info'ya yazmayabiliyor.

# Output tiplerini float varsayalım (Sentis'te çoğu blaze output float)
# Shape'i zorlamıyoruz; inference sonradan doldurabilir
g.output.extend([
    helper.make_tensor_value_info(BOXES_NAME,  onnx.TensorProto.FLOAT, None),
    helper.make_tensor_value_info(SCORES_NAME, onnx.TensorProto.FLOAT, None),
])

# (Opsiyonel ama faydalı) shape inference
try:
    m = shape_inference.infer_shapes(m)
except Exception as e:
    print("Shape inference hata verdi (önemli değil):", e)

onnx.save(m, OUT_PATH)
print("OK ->", OUT_PATH)
