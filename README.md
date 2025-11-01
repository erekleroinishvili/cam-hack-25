"# Cam Hack 2025" 

# 1) Install deps
pip install flask pillow numpy scikit-image

# 2) Start backend
python app.py

# 3) Open the UI
#   Double-click index.html (or open it in your browser)
#   Upload two images, tweak controls, hit Transform.
If your browser blocks cross-origin requests from a file:// page, you can instead visit http://127.0.0.1:5000/ and use a separate static server, or open index.html with a simple local server:
python -m http.server 8080 (then change fetch URL to http://127.0.0.1:5000/transform—already set).