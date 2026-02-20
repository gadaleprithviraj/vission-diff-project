# 🔍 Change Detection Algorithm (Python + OpenCV)

This project detects and highlights visual changes between two images of the same scene captured at different times.  
It uses a hybrid approach combining **SSIM (Structural Similarity Index)** and **pixel-wise absolute difference**, followed by **adaptive thresholding** and **morphological operations** to localize meaningful changes and ignore noise.

---

## 🚀 Features
- Detects structural and pixel-level changes between two images
- Highlights detected changes with bounding boxes
- Robust to lighting variations using SSIM
- Batch processing support for multiple image pairs
- Clean output formatting as per assignment / dataset requirement

---

## 🧠 How It Works
1. Convert both images to grayscale  
2. Compute SSIM difference to capture structural changes  
3. Combine SSIM diff with absolute pixel difference  
4. Apply adaptive thresholding to isolate changed regions  
5. Use morphological open/close to remove noise  
6. Find contours and draw bounding boxes on the "after" image  
7. Save outputs in the required format

---

## 🛠️ Tech Stack
- **Language:** Python  
- **Libraries:**  
  - OpenCV (cv2)  
  - NumPy  
  - scikit-image (SSIM)  
  - OS (file handling)

---

## 📁 Folder Structure


├── input/
│   ├── image1.jpg
│   ├── image1~2.jpg
│   ├── image2.jpg
│   ├── image2~2.jpg
│   ├── image3.jpg
│   ├── image3~2.jpg
├── task_2_output/
│   ├── image1.jpg
│   ├── image1~3.jpg
│   ├── image2.jpg
│   ├── image2~3.jpg
│   ├── image3.jpg
│   ├── image3~3.jpg
├── main.py
├── requirements.txt
└── README.md


**Naming Convention**
- `image.jpg`  → Before image  
- `image~2.jpg` → After image  
- Output:
  - `image.jpg` → Original before image  
  - `image~3.jpg` → Annotated image with detected changes  

---

## ⚙️ Setup & Installation

pip install opencv-python numpy scikit-image

▶️ How to Run

Place image pairs in the input/ folder:

sample.jpg

sample~2.jpg

Run the script:

python main.py

Output will be saved in:

task_2_output/

📌 Use Cases
- Surveillance change detection
- Infrastructure inspection (before vs after)
- Document tampering detection
- Quality control
- Scene monitoring & anomaly detection

📈 Improvements (Future Scope)
- *Real-time video change detection
- *Heatmap visualization of changes
- *Adjustable sensitivity thresholds
- *Deep learning-based segmentation
- *GUI / Web interface for uploads

🧑‍💻 Author

Developed by Sumit Gomes
Final Year Project / Computer Vision Assignment

📜 License

This project is licensed under the MIT License.
