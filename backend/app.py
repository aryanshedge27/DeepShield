import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from models    import db, MediaRecord
from detector  import analyse_image, analyse_video
from blockchain import register_hash, verify_hash

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"]         = os.getenv("DATABASE_URL", "sqlite:///deepfake.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]  = False
app.config["MAX_CONTENT_LENGTH"]              = 100 * 1024 * 1024  # 100 MB

db.init_app(app)

ALLOWED_IMAGES = {"jpg", "jpeg", "png", "webp", "bmp"}
ALLOWED_VIDEOS = {"mp4", "avi", "mov", "mkv", "webm"}

with app.app_context():
    db.create_all()


def allowed_ext(filename: str):
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext in ALLOWED_IMAGES:
        return ext, "image"
    if ext in ALLOWED_VIDEOS:
        return ext, "video"
    return None, None


# ── POST /analyse ────────────────────────────────────────────────────────────
@app.route("/analyse", methods=["POST"])
def analyse():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    f    = request.files["file"]
    ext, media_type = allowed_ext(f.filename)
    if not ext:
        return jsonify({"error": "Unsupported file type"}), 415

    data = f.read()

    # ── AI detection
    if media_type == "image":
        result = analyse_image(data)
    else:
        result = analyse_video(data)

    sha256 = result["sha256"]

    # ── Check if already in DB
    existing = MediaRecord.query.filter_by(sha256=sha256).first()
    if existing:
        chain = verify_hash(sha256)
        return jsonify({
            "cached":  True,
            "analysis": existing.to_dict(),
            "chain":    chain,
        })

    # ── Register on blockchain
    metadata = {
        "filename":   f.filename,
        "media_type": media_type,
        "verdict":    result["verdict"],
        "fake_score": result["fake_score"],
    }
    chain_result = register_hash(sha256, metadata)

    # ── Save to DB
    record = MediaRecord(
        sha256      = sha256,
        filename    = f.filename,
        media_type  = media_type,
        verdict     = result["verdict"],
        fake_score  = result["fake_score"],
        confidence  = result["confidence"],
        faces_found = result.get("faces_found", 0),
        chain_block = str(chain_result.get("block", chain_result.get("record", {}).get("block", ""))),
        chain_tx    = chain_result.get("tx_hash", ""),
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({
        "cached":   False,
        "analysis": record.to_dict(),
        "chain":    chain_result,
        "detail":   result,
    })


# ── POST /verify ─────────────────────────────────────────────────────────────
@app.route("/verify", methods=["POST"])
def verify():
    body   = request.get_json(silent=True) or {}
    sha256 = body.get("sha256", "").strip()
    if len(sha256) != 64:
        return jsonify({"error": "Provide a valid sha256 hex string"}), 400

    chain  = verify_hash(sha256)
    record = MediaRecord.query.filter_by(sha256=sha256).first()
    return jsonify({
        "chain":   chain,
        "db_record": record.to_dict() if record else None,
    })


# ── GET /history ─────────────────────────────────────────────────────────────
@app.route("/history", methods=["GET"])
def history():
    page    = request.args.get("page", 1, type=int)
    records = MediaRecord.query.order_by(MediaRecord.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return jsonify({
        "items": [r.to_dict() for r in records.items],
        "total": records.total,
        "pages": records.pages,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)