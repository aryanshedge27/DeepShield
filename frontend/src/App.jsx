import { useState } from "react";
import Uploader  from "./components/Uploader";
import ResultCard from "./components/ResultCard";
import Verifier  from "./components/Verifier";

export default function App() {
  const [result, setResult] = useState(null);

  return (
    <div style={{
      maxWidth: 680, margin: "0 auto",
      padding: "40px 20px",
      fontFamily: "system-ui, sans-serif",
    }}>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 4 }}>
        🛡️ Deepfake Detector
      </h1>
      <p style={{ color: "#6b7280", marginBottom: 32 }}>
        AI analysis + blockchain proof of authenticity
      </p>

      <Uploader onResult={setResult} />
      {result && <ResultCard data={result} />}
      <Verifier />
    </div>
  );
}