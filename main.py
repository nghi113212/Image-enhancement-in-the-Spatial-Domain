import cv2
import numpy as np
import matplotlib as plt
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk

# Biến lưu ảnh gốc
img_original = None

def open_image():
    global img_original
    file_path = filedialog.askopenfilename()
    if file_path:
        img_original = cv2.imread(file_path)
        img_original = cv2.cvtColor(img_original, cv2.COLOR_BGR2RGB)
        display_image(img_original, panel1, size=(300, 200))  

def display_image(img, panel, size):
    img = Image.fromarray(img)
    img = img.resize(size)  
    img_tk = ImageTk.PhotoImage(img)
    panel.config(image=img_tk)
    panel.image = img_tk

def negative_image():
    global img_original, img
    if img_original is not None:
        img = 255 - img_original  
        display_image(img, panel2, size=(830, 600)) 
    else:
        tk.messagebox.showwarning("Cảnh báo", "Vui lòng chọn ảnh trước!")


def apply_changes():
    """ Áp dụng các biến đổi ảnh theo thanh trượt """
    global img_original, img
    if img_original is None:
        tk.messagebox.showwarning("Cảnh báo", "Vui lòng chọn ảnh trước!")
        return

    img = img_original.copy()

    # Biến đổi Log
    c_log = log_var.get()
    if c_log > 0:
        img = log_transform(img, c_log)

     # Biến đổi Piecewise-Linear
    low = piecewise_low_var.get()  # Hệ số thấp
    high = piecewise_high_var.get()  # Hệ số cao
    if low > 0 or high > 0:
        img = piecewise_linear_transform(img, low, high)

    # Biến đổi Gamma
    c_gamma = gamma_c_var.get()
    gamma = gamma_var.get()
    if gamma > 0:
        img = gamma_transform(img, c_gamma, gamma)

    # Làm trơn ảnh (trung bình)
    ksize_avg = int(avg_filter_var.get())
    if ksize_avg > 1  : #and ksize_avg % 2 == 1
        img = cv2.blur(img, (ksize_avg, ksize_avg))

    # Làm trơn ảnh (Gauss)
    ksize_gauss = int(gauss_filter_var.get())
    sigma_gauss = gauss_sigma_var.get()
    if ksize_gauss > 1 and ksize_gauss % 2 ==1:
        img = cv2.GaussianBlur(img, (ksize_gauss, ksize_gauss), sigma_gauss)

    # Làm trơn ảnh (trung vị)
    ksize_median = int(median_filter_var.get())  #ksize = bộ lọc kenel 
    if ksize_median > 1 and ksize_median % 2 ==1:
        img = cv2.medianBlur(img, ksize_median)

    # Cân bằng sáng Histogram
    if hist_eq_var.get() > 0:
        img = histogram_equalization(img)

    # Hiển thị kết quả
    display_image(img, panel2, size=(830, 600))

def log_transform(img, c):
    img = np.clip(c * np.log(img.astype(np.float32) + 1), 0, 255)
    return img.astype(np.uint8)

def piecewise_linear_transform(img, low, high):
    # Chuẩn hóa giá trị pixel (0-255)
    img = img.astype(np.float32)
    
    # Điểm chia (breakpoints)
    breakpoint_high = 127
    
    # Áp dụng biến đổi piecewise-linear
    img = np.clip(np.where(
        img < breakpoint_high,
        low * img,  # Áp dụng hệ số thấp cho đoạn [0, 127]
        high * (img - breakpoint_high) + breakpoint_high  # Áp dụng hệ số cao cho đoạn [127, 255]
    ), 0, 255)
    
    return img.astype(np.uint8)

def gamma_transform(img, c, gamma):
    img = np.clip(c * (img / 255.0) ** gamma * 255, 0, 255)
    return img.astype(np.uint8)

def histogram_equalization(img):
    img_yuv = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
    return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2RGB)


def save_image():
    if img_original is None:
        tk.messagebox.showwarning("Cảnh báo", "Vui lòng chọn ảnh trước!")
        return

    # Mở hộp thoại lưu file
    file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("BMP", "*.bmp")])
    
    if file_path:
        # Lưu ảnh đã xử lý
        img_to_save = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # Đảm bảo chuyển đổi lại về BGR
        cv2.imwrite(file_path, img_to_save)
        tk.messagebox.showinfo("Thông báo", "Ảnh đã được lưu thành công!")



###########################################################################################################

root=tk.Tk()
root.title("Image Processing GUI")
#root.state("zoomed")

############################################################################################################
# Các nút chức năng
frame_buttons = tk.Frame(root, relief=tk.GROOVE, borderwidth=3)
frame_buttons.grid(row=0, column=0, pady=10, padx=5)

btn_open = ttk.Button(frame_buttons, text="Chọn ảnh", command=open_image)
btn_open.pack(side="left", padx=5, pady=5)

btn_update = ttk.Button(frame_buttons, text="Áp dụng", command=apply_changes)############ Chú ý cần sửa thêm
btn_update.pack(side="left", padx=5, pady=5)

btn_save = ttk.Button(frame_buttons, text="Lưu ra file", command=save_image)
btn_save.pack(side="left", padx=5, pady=5)

btn_close = ttk.Button(frame_buttons, text="Close", command=root.quit)
btn_close.pack(side="left", padx=5, pady=5)

# Khung công cụ
frame_left = tk.Frame(root, relief=tk.GROOVE, borderwidth=3)
frame_left.grid(row=1, column=0, padx=10, pady=10, sticky="n")

label_title = tk.Label(frame_left, text="Công cụ biến đổi", font=("Arial", 12, "bold"), fg="blue")
label_title.pack()


# Biến lưu giá trị thanh trượt
log_var = tk.DoubleVar(value=0)
piecewise_low_var=tk.DoubleVar(value=0)
piecewise_high_var=tk.DoubleVar(value=0)
gamma_c_var = tk.DoubleVar(value=0)
gamma_var = tk.DoubleVar(value=0)
avg_filter_var = tk.DoubleVar(value=0)
gauss_filter_var = tk.DoubleVar(value=0)
gauss_sigma_var = tk.DoubleVar(value=0)
median_filter_var = tk.DoubleVar(value=0)
hist_eq_var = tk.DoubleVar(value=0)

options = [
    ("Biến đổi Log", "Hệ số C", log_var, (0, 100)),
    ("Biến đổi Piecewise-Linear", "Hệ số thấp", piecewise_low_var,(0,100), "Hệ số cao" , piecewise_high_var, (0,100)),
    ("Biến đổi Gamma", "Hệ số C", gamma_c_var, (0, 100), "Gamma", gamma_var, (0, 100)),
    ("Làm trơn ảnh (lọc trung bình)", "Kích thước lọc", avg_filter_var, (0, 100)),
    ("Làm trơn ảnh (lọc Gauss)", "Kích thước lọc", gauss_filter_var, (0, 100), "Hệ số Sigma", gauss_sigma_var, (0, 100)),
    ("Làm trơn ảnh (lọc trung vị)", "Kích thước lọc", median_filter_var, (0, 100)),
    ("Cân bằng sáng dùng Histogram", "Giá trị", hist_eq_var, (0, 100))
]

colors = ["#66ccff", "#9933cc", "#ff9933", "#ff33cc", "#ff6600", "#ff00ff", "#ffcc00"]

for i, (title, *params) in enumerate(options):
    frame = tk.Frame(frame_left, bg=colors[i], padx=5, pady=2)
    frame.pack(fill="x", pady=5, padx=5)
    
    frame.columnconfigure(1, weight=1)
    label = tk.Label(frame, text=title, font=("Arial", 10, "bold"), bg=colors[i])
    label.grid(row=0, column=0, sticky="w", padx=5) 

    for j in range(0, len(params), 3):
        desc, param_var, (p_min, p_max) = params[j], params[j + 1], params[j + 2]

        label_param = tk.Label(frame, text=desc, bg=colors[i])
        label_param.grid(row=j + 1, column=0, sticky="w", padx=5, pady=2)
        
        scale = ttk.Scale(frame, from_=p_min, to=p_max, orient="horizontal", variable=param_var)
        scale.grid(row=j + 1, column=1, sticky="e", padx=5, pady=2)

# Tạo một style mới cho nút bấm và thay đổi kích thước chữ
style = ttk.Style()
style.configure("Large.TButton", font=("Arial", 18, "bold"))  # Chữ lớn và in đậm
btn_nagetiveImg = ttk.Button(root, text="Nagative Image", style="Large.TButton", command=negative_image)
btn_nagetiveImg.grid(padx=10, pady=10)
###################################################################################################################

# Khung hiển thị ảnh
frame_right = tk.Frame(root,relief=tk.GROOVE, borderwidth=3)
frame_right.grid(row=1, rowspan=10, column=1, padx=2, pady=10, sticky="n")

panel1 = tk.Label(frame_right)
panel1.pack()

frame_ImgResult = tk.Frame(root,relief=tk.GROOVE, borderwidth=3)
frame_ImgResult.grid(row=1, rowspan=10, column=2, padx=5, pady=10, sticky="n")

panel2 = tk.Label(frame_ImgResult)
panel2.pack()

root.mainloop()


