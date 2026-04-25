import torch
import torch.nn as nn
import timm
import numpy as np
import cv2
from PIL import Image
from torchvision import transforms
from facenet_pytorch import MTCNN
import hashlib, io

# ── Model ────────────────────────────────────────────────────────────────────
class DeepfakeDetector(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = timm.create_model(
            "efficientnet_b4", pretrained=True, num_classes=0
        )
        self.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(self.backbone.num_features, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        feats = self.backbone(x)
        return self.classifier(feats)


# ── Global singletons ─────────────────────────────────────────────────────────
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model  = DeepfakeDetector().to(device).eval()
mtcnn  = MTCNN(keep_all=True, device=device)

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


# ── Helpers ───────────────────────────────────────────────────────────────────
def compute_sha256(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def extract_faces(img_rgb: np.ndarray):
    """Return list of cropped face PIL images (may be empty)."""
    pil = Image.fromarray(img_rgb)
    boxes, _ = mtcnn.detect(pil)
    if boxes is None:
        return []
    faces = []
    h, w = img_rgb.shape[:2]
    for box in boxes:
        x1, y1, x2, y2 = [max(0, int(v)) for v in box]
        crop = img_rgb[y1:y2, x1:x2]
        if crop.size > 0:
            faces.append(Image.fromarray(crop))
    return faces


def analyse_faces(faces) -> float:
    """Return mean fake-probability across detected faces."""
    if not faces:
        return 0.5  # indeterminate — no face found
    scores = []
    with torch.no_grad():
        for face in faces:
            t = transform(face).unsqueeze(0).to(device)
            score = model(t).item()
            scores.append(score)
    return float(np.mean(scores))


# ── Public API ────────────────────────────────────────────────────────────────
def analyse_image(file_bytes: bytes) -> dict:
    arr   = np.frombuffer(file_bytes, dtype=np.uint8)
    img   = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    img   = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    faces = extract_faces(img)
    score = analyse_faces(faces)
    sha   = compute_sha256(file_bytes)
    return {
        "sha256":       sha,
        "faces_found":  len(faces),
        "fake_score":   round(score, 4),
        "verdict":      "FAKE" if score > 0.5 else "AUTHENTIC",
        "confidence":   round(abs(score - 0.5) * 2, 4),  # 0..1
    }


def analyse_video(file_bytes: bytes, max_frames: int = 20) -> dict:
    """Sample frames, run image detector on each, aggregate."""
    sha = compute_sha256(file_bytes)
    tmp = "/tmp/_deepfake_tmp.mp4"
    with open(tmp, "wb") as f:
        f.write(file_bytes)

    cap    = cv2.VideoCapture(tmp)
    total  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step   = max(1, total // max_frames)
    scores = []

    for i in range(0, total, step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = extract_faces(frame)
        scores.append(analyse_faces(faces))

    cap.release()
    mean_score = float(np.mean(scores)) if scores else 0.5
    return {
        "sha256":        sha,
        "frames_checked": len(scores),
        "fake_score":    round(mean_score, 4),
        "verdict":       "FAKE" if mean_score > 0.5 else "AUTHENTIC",
        "confidence":    round(abs(mean_score - 0.5) * 2, 4),
        "frame_scores":  [round(s, 3) for s in scores],
    }