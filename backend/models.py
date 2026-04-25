from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class MediaRecord(db.Model):
    __tablename__ = "media_records"

    id          = db.Column(db.Integer, primary_key=True)
    sha256      = db.Column(db.String(64), unique=True, nullable=False, index=True)
    filename    = db.Column(db.String(255), nullable=False)
    media_type  = db.Column(db.String(10))          # "image" | "video"
    verdict     = db.Column(db.String(10))          # "FAKE"  | "AUTHENTIC"
    fake_score  = db.Column(db.Float)
    confidence  = db.Column(db.Float)
    faces_found = db.Column(db.Integer, default=0)
    chain_block = db.Column(db.String(128))
    chain_tx    = db.Column(db.String(128))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":          self.id,
            "sha256":      self.sha256,
            "filename":    self.filename,
            "media_type":  self.media_type,
            "verdict":     self.verdict,
            "fake_score":  self.fake_score,
            "confidence":  self.confidence,
            "faces_found": self.faces_found,
            "chain_block": self.chain_block,
            "chain_tx":    self.chain_tx,
            "created_at":  self.created_at.isoformat(),
        }