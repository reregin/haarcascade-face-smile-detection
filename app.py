import streamlit as st
import cv2
import os
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import av
import time

# --- 1. Pemuatan Model (Material Collecting) ---
@st.cache_resource
def load_cascades():
    """Memuat file XML Haar Cascade dari direktori data OpenCV."""
    cascade_dir = cv2.data.haarcascades
    
    face_cascade_path = os.path.join(cascade_dir, 'haarcascade_frontalface_default.xml')
    smile_cascade_path = os.path.join(cascade_dir, 'haarcascade_smile.xml')

    if not os.path.exists(face_cascade_path):
        st.error(f"Error: File cascade wajah tidak ditemukan di {face_cascade_path}")
        return None, None
        
    if not os.path.exists(smile_cascade_path):
        st.error(f"Error: File cascade senyum tidak ditemukan di {smile_cascade_path}")
        return None, None

    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    smile_cascade = cv2.CascadeClassifier(smile_cascade_path)
    
    return face_cascade, smile_cascade

face_cascade, smile_cascade = load_cascades()

# --- 2. Pemrosesan Video (Assembly) ---
class FaceSmileProcessor(VideoProcessorBase):
    def __init__(self):
        self.face_cascade = face_cascade
        self.smile_cascade = smile_cascade
        
        # Inisialisasi prev_frame_time
        self.prev_frame_time = time.time() 

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        """
        Menerima frame, memprosesnya, dan mengembalikannya.
        """
        if self.face_cascade is None or self.smile_cascade is None:
            return frame

        img = frame.to_ndarray(format="bgr24")

        # Logika Penghitungan FPS
        new_frame_time = time.time()
        
        # Hindari pembagian dengan nol jika delta waktu terlalu kecil
        time_diff = new_frame_time - self.prev_frame_time
        if time_diff > 0:
            fps = 1 / time_diff
        else:
            fps = 0
            
        self.prev_frame_time = new_frame_time
        fps = int(fps)

        # Tampilkan FPS di frame
        # (Posisi (10, 30), Font, Skala 1, Warna Hijau, Ketebalan 2)
        cv2.putText(img, f"FPS: {fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # --- Logika Deteksi Asli ---
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(30, 30)
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(img, 'Wajah', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]

            smiles = self.smile_cascade.detectMultiScale(
                roi_gray,
                scaleFactor=1.8, 
                minNeighbors=20,
                minSize=(25, 25)
            )

            for (sx, sy, sw, sh) in smiles:
                cv2.rectangle(roi_color, (sx, sy), (sx+sw, sy+sh), (0, 255, 0), 2)
                cv2.putText(img, 'Senyum', (x + sx, y + sy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        # --- Akhir Logika Deteksi ---

        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 3. Antarmuka Pengguna (UI) Streamlit ---

st.set_page_config(page_title="Deteksi Wajah & Senyum Real-Time", layout="centered")
st.title("🎭 Deteksi Wajah dan Senyum Real-Time")
st.write(
    "Aplikasi ini menggunakan metode **Haar Cascade** berbasis OpenCV untuk "
    "mendeteksi wajah dan senyum secara *real-time* dari webcam Anda."
)

rtc_config = RTCConfiguration({
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
})

if face_cascade is not None and smile_cascade is not None:
    st.write("Tekan **'START'** untuk mengaktifkan kamera Anda dan memulai deteksi.")
    
    webrtc_streamer(
        key="face-smile-detection",
        video_processor_factory=FaceSmileProcessor,
        media_stream_constraints={"video": True, "audio": False},
        rtc_configuration=rtc_config,
        async_processing=True,
    )
else:
    st.error("Gagal memuat model Haar Cascade. Aplikasi tidak dapat dimulai.")

st.caption("Dikembangkan oleh Triadi M, Natalio Tumuahi, dan Regina George")