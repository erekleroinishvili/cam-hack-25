"# Cam Hack 2025" 

# 1) Install deps
pip install flask pillow numpy scikit-image

# 2) Start backend
python app.py

# 3) Open the UI
#   Double-click index.html (or open it in your browser)
#   Upload two images, tweak controls, hit Transform.
Visit http://127.0.0.1:5000/ui



This is a small demo web app that rearranges the pixels of one image to look like another, without changing any pixel values.
It uses a simple Flask backend for the transformation and an HTML/JS front-end for uploads.

1. Install dependencies
pip install flask pillow numpy scikit-image


(If you get any import errors later, rerun the above.)

2. Start the backend server
python app.py


You should see something like:

 * Running on http://127.0.0.1:5000


Keep this terminal window open while you use the app.

3. Open the web interface

Now that Flask serves the front-end directly, you don’t need to open index.html manually.

In your browser, go to:
👉 http://127.0.0.1:5000/ui

You’ll see the interface with three panels:

Source image (pixels we’ll reuse)

Target image (the look-alike)

Output (the rearranged result)

Upload two images, adjust the sliders (max_side, xy_weight), and click Transform.
The result appears on the right.

4. What happens under the hood

Flask’s /transform route receives both images and performs the permutation.

Flask’s new /ui route serves the index.html file so everything is on the same origin (127.0.0.1:5000) — no CORS errors.

The browser fetches /transform with your uploaded files and displays the returned PNG.

5. (Optional) Command-line test

If you want to verify the backend alone:

curl -X POST http://127.0.0.1:5000/transform
  -F src=@source.jpg \
  -F tgt=@target.jpg \
  -F max_side=256 \
  -F xy_weight=0.25 \
  --output out.png


You’ll get an out.png file containing the permuted image.