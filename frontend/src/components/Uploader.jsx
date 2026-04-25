import { useState, useCallback } from "react";
import { analyseMedia } from "../api";

export default function Uploader({ onResult }) {
  const [dragging, setDragging] = useState(false);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState(null);

  const handle = useCallback(async (file) => {
    if (!file) return;
    setError(null);
    setLoading(true);
    try {
      const data = await analyseMedia(file);
      onResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [onResult]);

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handle(e.dataTransfer.files[0]);
  };

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
      onClick={() => document.getElementById("file-in").click()}
      style={{
        border:        `2px dashed ${dragging ? "#6366f1" : "#d1d5db"}`,
        borderRadius:  "16px",
        padding:       "48px 24px",
        textAlign:     "center",
        cursor:        "pointer",
        transition:    "border-color 0.2s",
        background:    dragging ? "#eef2ff" : "transparent",
      }}
    >
      <input
        id="file-in"
        type="file"
        accept="image/*,video/*"
        style={{ display: "none" }}
        onChange={(e) => handle(e.target.files[0])}
      />
      {loading ? (
        <p style={{ color: "#6366f1", fontWeight: 500 }}>⏳ Analysing…</p>
      ) : (
        <>
          <p style={{ fontSize: 32, margin: 0 }}>🎞️</p>
          <p style={{ marginTop: 12, color: "#374151", fontWeight: 500 }}>
            Drop an image or video here
          </p>
          <p style={{ color: "#9ca3af", fontSize: 14 }}>
            JPG · PNG · MP4 · MOV — up to 100 MB
          </p>
        </>
      )}
      {error && <p style={{ color: "#ef4444", marginTop: 8 }}>{error}</p>}
    </div>
  );
}