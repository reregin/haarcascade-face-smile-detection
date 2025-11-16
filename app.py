import streamlit as st
import cv2
import os
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import av

# --- 1. Pemuatan Model (Material Collecting) ---
@st.cache_resource
def load_cascades():
    """Memuat file XML Haar Cascade dari direktori data OpenCV."""
    cascade_dir = cv2.data.haarcascades
    
    # Path untuk detektor wajah
    face_cascade_path = os.path.join(cascade_dir, 'haarcascade_frontalface_default.xml')
    # Path untuk detektor senyum
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

# Muat model saat aplikasi dimulai
face_cascade, smile_cascade = load_cascades()

# --- 2. Pemrosesan Video (Assembly) ---
class FaceSmileProcessor(VideoProcessorBase):
    def __init__(self):
        self.face_cascade = face_cascade
        self.smile_cascade = smile_cascade

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        """
        Menerima frame, memprosesnya, dan mengembalikannya.
        """
        if self.face_cascade is None or self.smile_cascade is None:
            return frame

        # Konversi av.VideoFrame ke format NumPy (BGR)
        img = frame.to_ndarray(format="bgr24")

        # --- Logika Deteksi Asli ---
        
        # 1. Konversi ke Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 2. Deteksi Wajah
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(30, 30)
        )

        # 3. Deteksi Senyum (di dalam ROI Wajah)
        for (x, y, w, h) in faces:
            # Gambar kotak biru untuk Wajah
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(img, 'Wajah', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            # === MENGGUNAKAN ROI WAJAH PENUH (sesuai permintaan) ===
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w] # Ini adalah "view" dari img

            # Deteksi senyum hanya di dalam ROI wajah
            smiles = self.smile_cascade.detectMultiScale(
                roi_gray,
                # === MENGGUNAKAN PARAMETER ASLI (sesuai permintaan) ===
                scaleFactor=1.8, 
                minNeighbors=20,
                minSize=(25, 25)
            )

            # Gambar kotak hijau untuk Senyum
            for (sx, sy, sw, sh) in smiles:
                # Koordinat digambar relatif terhadap roi_color
                cv2.rectangle(roi_color, (sx, sy), (sx+sw, sy+sh), (0, 255, 0), 2)
                # Tambahkan label 'Senyum' pada frame utama
                cv2.putText(img, 'Senyum', (x + sx, y + sy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # --- Akhir Logika Deteksi ---

        # Konversi kembali frame NumPy (BGR) yang telah diproses ke av.VideoFrame
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 3. Antarmuka Pengguna (UI) Streamlit ---

st.set_page_config(page_title="Deteksi Wajah & Senyum Real-Time", layout="centered")
st.title("🎭 Deteksi Wajah dan Senyum Real-Time")
st.write(
    "Aplikasi ini menggunakan metode **Haar Cascade** berbasis OpenCV untuk "
    "mendeteksi wajah dan senyum secara *real-time* dari webcam Anda."
)

# Konfigurasi RTC untuk deployment
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