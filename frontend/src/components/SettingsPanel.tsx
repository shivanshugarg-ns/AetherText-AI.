import React from "react";

interface Props {
  modelHint: string;
  streaming: boolean;
  setStreaming: (v: boolean) => void;
  streamingSupported: boolean;
}

export default function SettingsPanel({
  modelHint,
  streaming,
  setStreaming,
  streamingSupported,
}: Props) {
  return (
    <div className="panel">
      <h3>Settings</h3>
      <p className="meta small">{modelHint}</p>

      <div className="field-inline" style={{ marginTop: 12 }}>
        <label className="switch">
          <input
            type="checkbox"
            checked={streaming && streamingSupported}
            onChange={(e) => setStreaming(e.target.checked)}
            disabled={!streamingSupported}
          />
          <span>Use streaming</span>
        </label>
        {!streamingSupported && (
          <span className="hint">Streaming not supported in this browser.</span>
        )}
      </div>
    </div>
  );
}
