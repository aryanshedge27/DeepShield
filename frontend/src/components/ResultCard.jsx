export default function ResultCard({ data }) {
  const { analysis, chain, detail } = data;
  const isFake   = analysis.verdict === "FAKE";
  const pct      = Math.round((analysis.fake_score ?? 0) * 100);
  const conf     = Math.round((analysis.confidence ?? 0) * 100);

  return (
    <div style={{
      borderRadius: 16,
      border: `2px solid ${isFake ? "#fca5a5" : "#6ee7b7"}`,
      padding: "24px",
      marginTop: "24px",
      background: isFake ? "#fff1f2" : "#f0fdf4",
    }}>
      {/* Verdict badge */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
        <span style={{
          fontSize: 28,
          background: isFake ? "#ef4444" : "#10b981",
          color: "#fff",
          borderRadius: 8,
          padding: "4px 16px",
          fontWeight: 700,
          letterSpacing: 2,
        }}>
          {analysis.verdict}
        </span>
        <span style={{ color: "#6b7280", fontSize: 14 }}>
          {conf}% confidence · {analysis.faces_found} face(s) found
        </span>
      </div>

      {/* Fake score bar */}
      <p style={{ fontSize: 13, color: "#6b7280", marginBottom: 4 }}>Fake probability</p>
      <div style={{
        background: "#e5e7eb", borderRadius: 99, height: 10, marginBottom: 16
      }}>
        <div style={{
          width: `${pct}%`,
          height: 10,
          borderRadius: 99,
          background: isFake
            ? "linear-gradient(90deg,#f87171,#ef4444)"
            : "linear-gradient(90deg,#6ee7b7,#10b981)",
          transition: "width 0.6s ease",
        }} />
      </div>

      {/* SHA-256 */}
      <p style={{ fontSize: 12, color: "#9ca3af", wordBreak: "break-all", margin: "8px 0 0" }}>
        <strong>SHA-256</strong> {analysis.sha256}
      </p>

      {/* Blockchain proof */}
      <div style={{
        marginTop: 16, padding: "12px 16px",
        background: "#f8fafc", borderRadius: 10,
        border: "1px solid #e2e8f0",
      }}>
        <p style={{ margin: 0, fontWeight: 600, fontSize: 14 }}>⛓️ Blockchain Proof</p>
        {chain?.record ? (
          <>
            <p style={{ fontSize: 12, color: "#6b7280", margin: "4px 0 0" }}>
              Block: <code>{chain.record.block}</code>
            </p>
            <p style={{ fontSize: 12, color: "#6b7280", margin: 2 }}>
              Registered: {new Date(chain.record.timestamp * 1000).toLocaleString()}
            </p>
          </>
        ) : chain?.tx_hash ? (
          <p style={{ fontSize: 12, color: "#6b7280", margin: "4px 0 0" }}>
            Tx: <code>{chain.tx_hash}</code> · Block #{chain.block}
          </p>
        ) : (
          <p style={{ fontSize: 12, color: "#9ca3af", margin: "4px 0 0" }}>
            {data.cached ? "Already on-chain ✓" : "Registering…"}
          </p>
        )}
      </div>

      {/* Frame scores for video */}
      {detail?.frame_scores?.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <p style={{ fontSize: 13, fontWeight: 600 }}>Frame-by-frame scores</p>
          <div style={{ display: "flex", gap: 3, flexWrap: "wrap" }}>
            {detail.frame_scores.map((s, i) => (
              <div key={i} title={`Frame ${i+1}: ${(s*100).toFixed(1)}%`}
                style={{
                  width: 18, height: 18, borderRadius: 4,
                  background: s > 0.5 ? `rgba(239,68,68,${s})` : `rgba(16,185,129,${1-s})`,
                }} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}