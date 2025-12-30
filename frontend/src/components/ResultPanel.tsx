import React from "react";
import { AIResponse } from "../api/types";

interface Props {
  output: string;
  status: "idle" | "streaming" | "error" | "done";
  error: string | null;
  meta: AIResponse | null;
  onStop: () => void;
  isStreaming: boolean;
}

export default function ResultPanel({
  output,
  status,
  error,
  meta,
  onStop,
  isStreaming,
}: Props) {
  return (
    <div className="panel output">
      <div className="section-head">
        <div>
          <h3>Output</h3>
          <p className="meta small">Status: {status}</p>
        </div>
        {isStreaming && (
          <button type="button" className="secondary" onClick={onStop}>
            Stop
          </button>
        )}
      </div>

      {error && <div className="alert">{error}</div>}

      <div className="result-box">
        {output || (status === "streaming" ? "Streaming..." : "Results will appear here.")}
      </div>

      {meta && (
        <div className="meta-row">
          <span className="badge">Model: {meta.model}</span>
          <span className="badge">Tokens: {meta.usage.total_tokens}</span>
          <span className="badge">Cost: ${meta.usage.estimated_cost.toFixed(6)}</span>
        </div>
      )}
    </div>
  );
}
