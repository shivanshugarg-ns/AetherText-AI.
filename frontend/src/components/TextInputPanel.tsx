import React, { ChangeEvent } from "react";
import { TaskType } from "../api/types";

interface Props {
  task: TaskType;
  setTask: (t: TaskType) => void;
  inputText: string;
  setInputText: (v: string) => void;
  targetLanguage: string;
  setTargetLanguage: (v: string) => void;
  temperature: number;
  setTemperature: (v: number) => void;
  maxTokens: number;
  setMaxTokens: (v: number) => void;
  onSubmit: () => void;
  onClear: () => void;
  streaming: boolean;
  setStreaming: (v: boolean) => void;
  streamingSupported: boolean;
  disableSubmit: boolean;
}

const languages = ["English", "Spanish", "French", "German", "Hindi", "Chinese"];

export default function TextInputPanel(props: Props) {
  const {
    task,
    setTask,
    inputText,
    setInputText,
    targetLanguage,
    setTargetLanguage,
    temperature,
    setTemperature,
    maxTokens,
    setMaxTokens,
    onSubmit,
    onClear,
    streaming,
    setStreaming,
    streamingSupported,
    disableSubmit,
  } = props;

  return (
    <div className="panel">
      <div className="field-group">
        <label>Task</label>
        <div className="chip-row">
          {["summarize", "translate", "generate"].map((t) => (
            <button
              key={t}
              type="button"
              className={`chip ${task === t ? "active" : ""}`}
              onClick={() => setTask(t as TaskType)}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {task === "translate" && (
        <div className="field-group">
          <label>Target language</label>
          <select
            value={targetLanguage}
            onChange={(e: ChangeEvent<HTMLSelectElement>) =>
              setTargetLanguage(e.target.value)
            }
          >
            {languages.map((lang) => (
              <option key={lang} value={lang}>
                {lang}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="field-group">
        <label>Input</label>
        <textarea
          value={inputText}
          onChange={(e: ChangeEvent<HTMLTextAreaElement>) =>
            setInputText(e.target.value)
          }
          rows={10}
          placeholder="Paste or type your content..."
        />
        <div className="meta small">{inputText.length} characters</div>
      </div>

      <div className="field-inline">
        <label className="switch">
          <input
            type="checkbox"
            checked={streaming && streamingSupported}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              setStreaming(e.target.checked)
            }
            disabled={!streamingSupported}
          />
          <span>Use streaming</span>
        </label>
        {!streamingSupported && (
          <span className="hint">Streaming not supported in this browser.</span>
        )}
      </div>

      <div className="field-group">
        <label>Temperature ({temperature.toFixed(2)})</label>
        <input
          type="range"
          min={0}
          max={1}
          step={0.05}
          value={temperature}
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            setTemperature(parseFloat(e.target.value))
          }
        />
      </div>

      <div className="field-group">
        <label>Max tokens ({maxTokens})</label>
        <input
          type="range"
          min={50}
          max={1200}
          step={50}
          value={maxTokens}
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            setMaxTokens(parseInt(e.target.value, 10))
          }
        />
      </div>

      <div className="buttons-row">
        <button type="button" className="cta" onClick={onSubmit} disabled={disableSubmit}>
          {disableSubmit ? "Running..." : "Generate"}
        </button>
        <button type="button" className="secondary" onClick={onClear}>
          Clear
        </button>
      </div>
    </div>
  );
}
