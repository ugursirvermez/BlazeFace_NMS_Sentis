import onnx
from onnx import shape_inference
from onnx.utils import extract_model

IN_PATH  = "blaze.onnx"
OUT_PATH = "blaze_raw_pruned.onnx"

# Netron'da NonMaxSuppression input'larından kopyaladığın isimler:
BOXES_NAME  = "finalBoxesCoords"
SCORES_NAME = "finalScores_T"

m = onnx.load(IN_PATH)

# Model input isimlerini otomatik alalım (genelde 1 input var)
input_names = [i.name for i in m.graph.input]
print("Model inputs:", input_names)

# Çıkış olarak NMS öncesi iki tensörü vereceğiz
output_names = [BOXES_NAME, SCORES_NAME]
print("Requested outputs:", output_names)

# ✅ Asıl olay: subgraph çıkar (NMS artık modelde bulunmayacak)
extract_model(IN_PATH, OUT_PATH, input_names, output_names)

# (opsiyonel) shape inference
try:
    m2 = onnx.load(OUT_PATH)
    m2 = shape_inference.infer_shapes(m2)
    onnx.save(m2, OUT_PATH)
except Exception as e:
    print("Shape inference skipped:", e)

print("OK ->", OUT_PATH)

# Mini doğrulama: modelde NonMaxSuppression kaldı mı?
m3 = onnx.load(OUT_PATH)
has_nms = any(n.op_type == "NonMaxSuppression" for n in m3.graph.node)
print("Contains NonMaxSuppression?", has_nms)
