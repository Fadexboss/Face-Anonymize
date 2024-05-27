import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import filedialog, ttk
import os

mp_face_detection = mp.solutions.face_detection

# Video dosyasını seçme fonksiyonu
def select_video_file():
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4")])
    return file_path

# Video işleme fonksiyonu
def process_video(video_file, output_file, output_path):
    cap = cv2.VideoCapture(video_file)

    # Codec ve VideoWriter nesnesi tanımla
    codec = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 25  # FPS 25 olarak ayarlandı
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_path + "/" + output_file, codec, fps, (frame_width, frame_height))

    with mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5) as face_detection:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break

            # BGR görüntüyü RGB'ye dönüştür.
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = face_detection.process(image)

            # Yüz tespit açıklamalarını görüntüye çiz.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.detections:
                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = image.shape
                    x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(
                        bboxC.width * iw), int(bboxC.height * ih)

                    # Bölgenin görüntü sınırları içinde olmasını sağla
                    x = max(0, x)
                    y = max(0, y)
                    w = min(iw - x, w)
                    h = min(ih - y, h)

                    # Tespit edilen yüz bölgesini bulanıklaştır
                    face_region = image[y:y + h, x:x + w]
                    blurred_face = cv2.blur(face_region, (93, 93))
                    image[y:y + h, x:x + w] = blurred_face

            # Çerçeveyi çıkış dosyasına yaz
            out.write(image)

            # Çerçeveyi göster
            cv2.imshow('Sansürlü video', cv2.resize(image, (1280, 720)))
            # Çerçeveler arasında 40 ms bekle (1000 ms / 25 FPS = 40 ms)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cap.release()
                out.release()
                cv2.destroyAllWindows()
                return

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    # Kaydedilen video dosyasını aç
    saved_video = cv2.VideoCapture(output_path + "/" + output_file)
    while saved_video.isOpened():
        ret, frame = saved_video.read()
        if not ret:
            break
        cv2.imshow("Saved Video", frame)
        # Çerçeveler arasında 40 ms bekle (1000 ms / 25 FPS = 40 ms)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    saved_video.release()
    cv2.destroyAllWindows()

# Video işlemeyi başlatma fonksiyonu
def start_processing():
    video_file = select_video_file()
    if video_file:
        output_path = filedialog.askdirectory()
        if output_path:
            output_file = output_file_entry.get()
            if output_file:
                process_video(video_file, output_file + ".mp4", output_path)

# Bir klasördeki resimleri işleme fonksiyonu
def process_images_in_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        output_folder_path = filedialog.askdirectory()
        if output_folder_path:
            for filename in os.listdir(folder_path):
                if filename.endswith((".jpg", ".jpeg", ".png")):
                    image_path = os.path.join(folder_path, filename)
                    image = cv2.imread(image_path)

                    with mp_face_detection.FaceDetection(
                            model_selection=0, min_detection_confidence=0.5) as face_detection:
                        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        results = face_detection.process(image_rgb)

                        if results.detections:
                            for detection in results.detections:
                                bboxC = detection.location_data.relative_bounding_box
                                ih, iw, _ = image.shape
                                x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(
                                    bboxC.width * iw), int(bboxC.height * ih)

                                x = max(0, x)
                                y = max(0, y)
                                w = min(iw - x, w)
                                h = min(ih - y, h)

                                face_region = image[y:y + h, x:x + w]
                                blurred_face = cv2.blur(face_region, (93, 93))
                                image[y:y + h, x:x + w] = blurred_face

                        output_image_path = os.path.join(output_folder_path, filename)
                        cv2.imwrite(output_image_path, image)

color = "#DFBBC5"
# GUI kurulum
root = tk.Tk()
root.title("Video ve resimdeki yüzleri sansürleme")
root.geometry("600x600")
root.configure(bg=color)

# Arayüzü iki kısma ayırma
frame1 = tk.Frame(root, bg=color)
frame1.place(relx=0.5, rely=0.3, anchor="center")

frame2 = tk.Frame(root, bg=color)
frame2.place(relx=0.5, rely=0.7, anchor="center")

select_button = ttk.Button(frame1, text="Video seç", command=start_processing, style="TButton")
select_button.pack(side=tk.LEFT, padx=(0, 10))

# Etiket ve giriş alanını birlikte tutacak bir çerçeve ekleme
frame3 = tk.Frame(frame1, bg=color)
frame3.pack(side=tk.LEFT)

label = tk.Label(frame3, text="Video İsmi:", bg=color)
label.pack(side=tk.LEFT, padx=5)

output_file_entry = tk.Entry(frame3, width=40)
output_file_entry.pack(side=tk.LEFT)
output_file_entry.insert(0, "Video adını giriniz")

# Klasördeki resimleri işlemek için bir buton ekleme
select_image_folder_button = ttk.Button(frame2, text="Resim klasörü seç", command=process_images_in_folder,
                                        style="TButton")
select_image_folder_button.pack()

# Butonları stilize etme
style = ttk.Style()
style.configure("TButton", padding=6, relief="raised", background=color)

root.mainloop()
