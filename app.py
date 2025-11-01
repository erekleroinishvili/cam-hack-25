# app.py
from io import BytesIO
from flask import Flask, request, send_file, jsonify
from PIL import Image
import numpy as np
from flask import send_from_directory

try:
    from skimage.color import rgb2lab
    SKIMAGE_OK = True
except Exception:
    SKIMAGE_OK = False

app = Flask(__name__)

def to_lab01(rgb_uint8):
    """
    rgb_uint8: (H,W,3) uint8 in [0,255]
    returns lab01: (N,3) with L in [0,1], a,b roughly in [0,1]
    """
    rgb = rgb_uint8.astype(np.float32) / 255.0
    if SKIMAGE_OK:
        lab = rgb2lab(rgb)  # L in [0..100], a,b about [-128..127]
        L = lab[..., 0] / 100.0
        a = (lab[..., 1] + 128.0) / 255.0
        b = (lab[..., 2] + 128.0) / 255.0
        lab01 = np.stack([L, a, b], axis=-1)
    else:
        # Fallback: use normalized RGB as an OK-ish proxy if skimage isn't available
        lab01 = rgb
    return lab01.reshape(-1, 3)

def simple_sort_curve_permutation(src_rgb, tgt_rgb, xy_weight=0.25):
    """
    src_rgb, tgt_rgb: (H,W,3) uint8 arrays (same size).
    Returns output_rgb: (H,W,3) uint8 where pixels of src are permuted
    to resemble tgt (by sorted rank in LAB+XY).
    """
    H, W, _ = src_rgb.shape
    N = H * W

    src_lab = to_lab01(src_rgb)           # (N,3)
    tgt_lab = to_lab01(tgt_rgb)           # (N,3)

    # Normalized grid coordinates in [0,1]
    ys, xs = np.mgrid[0:H, 0:W]
    xs = (xs.astype(np.float32) / max(W - 1, 1)).reshape(-1, 1)
    ys = (ys.astype(np.float32) / max(H - 1, 1)).reshape(-1, 1)

    # Compose features and keys (linear 1D projection)
    src_feat = np.concatenate([src_lab, xy_weight * xs, xy_weight * ys], axis=1)  # (N,5)
    tgt_feat = np.concatenate([tgt_lab, xy_weight * xs, xy_weight * ys], axis=1)  # (N,5)

    # Single scalar key per pixel: dot with ones
    src_key = src_feat.sum(axis=1)
    tgt_key = tgt_feat.sum(axis=1)

    # Stable sorts for deterministic pairing
    order_s = np.argsort(src_key, kind="mergesort")
    order_t = np.argsort(tgt_key, kind="mergesort")

    src_flat = src_rgb.reshape(-1, 3)
    out_flat = np.empty_like(src_flat)

    # Pair by rank: the k-th smallest in source goes to the k-th smallest target position
    out_flat[order_t] = src_flat[order_s]

    return out_flat.reshape(H, W, 3)

def load_image(file_storage, max_side=None):
    im = Image.open(file_storage.stream).convert("RGB")
    if max_side:
        w, h = im.size
        s = max(w, h)
        if s > max_side:
            scale = max_side / float(s)
            im = im.resize((int(w*scale), int(h*scale)), Image.BILINEAR)
    return im

@app.route("/transform", methods=["POST"])
def transform_route():
    if "src" not in request.files or "tgt" not in request.files:
        return jsonify({"error": "Upload 'src' and 'tgt' image files"}), 400

    # Optional controls
    try:
        max_side = int(request.form.get("max_side", "256"))
    except:
        max_side = 256
    try:
        xy_weight = float(request.form.get("xy_weight", "0.25"))
    except:
        xy_weight = 0.25

    src_im = load_image(request.files["src"], max_side=max_side)
    tgt_im = load_image(request.files["tgt"], max_side=max_side)

    # Resize to exactly the same size (use target's size after its own scaling)
    tgt_size = tgt_im.size
    src_im = src_im.resize(tgt_size, Image.BILINEAR)

    src = np.array(src_im, dtype=np.uint8)
    tgt = np.array(tgt_im, dtype=np.uint8)
    out = simple_sort_curve_permutation(src, tgt, xy_weight=xy_weight)

    buf = BytesIO()
    Image.fromarray(out).save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

@app.route("/")
def index():
    return "Open index.html locally and it will POST to /transform on this server."

@app.route("/ui")
def ui():
    # Serve the index.html file from the current folder (".")
    return send_from_directory(".", "index.html")

if __name__ == "__main__":
    # Run: python app.py  (then open index.html in a browser)
    app.run(host="127.0.0.1", port=5000, debug=True)
