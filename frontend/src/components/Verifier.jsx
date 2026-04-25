import { useState } from "react";
import { verifyHash } from "../api";

export default function Verifier() {
  const [hash,   setHash]   = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const check = async () => {
    if (hash.trim().length !== 64) return;
    setLoading(true);
    const data = await verifyHash(hash.trim());
    setResult(data);
    setLoading(false);
  };

  return (
    <div style={{ marginTop: 32 }}>
      <h3 style={{ fontWeight: 600 }}>🔍 Verify by SHA-256</h3>
      <div style={{ display: "flex", gap: 8 }}>
        <input
          value={hash}
          onChange={(e) => setHash(e.target.value)}
          placeholder="Paste SHA-256 hash…"
          style={{
            flex: 1, padding: "10px 14px",
            borderRadius: 10, border: "1px solid #d1d5db",
            fontSize: 13, fontFamily: "monospace",
          }}
        />
        <button
          onClick={check}
          disabled={loading || hash.trim().length !== 64}
          style={{
            padding: "10px 20px", borderRadius: 10,
            background: "#6366f1", color: "#fff",
            fontWeight: 600, border: "none", cursor: "pointer",
          }}
        >
          {loading ? "…" : "Verify"}
        </button>
      </div>

      {result && (
        <div style={{
          marginTop: 16, padding: "16px",
          borderRadius: 12, background: result.chain?.found ? "#f0fdf4" : "#fff1f2",
          border: `1px solid ${result.chain?.found ? "#6ee7b7" : "#fca5a5"}`,
        }}>
          {result.chain?.found ? (
            <>
              <p style={{ fontWeight: 600, color: "#065f46" }}>✅ Authenticated on blockchain</p>
              <p style={{ fontSize: 13 }}>
                Registered: {new Date((result.chain.record?.timestamp ?? result.chain.timestamp) * 1000).toLocaleString()}
              </p>
              {result.db_record && (
                <p style={{ fontSize: 13 }}>
                  Verdict: <strong>{result.db_record.verdict}</strong> ({Math.round(result.db_record.fake_score * 100)}% fake)
                </p>
              )}
            </>
          ) : (
            <p style={{ fontWeight: 600, color: "#991b1b" }}>❌ Hash not found on blockchain</p>
          )}
        </div>
      )}
    </div>
  );
}