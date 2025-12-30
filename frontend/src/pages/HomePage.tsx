import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  sendAIRequest,
  streamAIRequest,
  getRecentUsage,
} from "../api/client";
import { AIRequest, AIResponse, TaskType, UsageHistoryItem } from "../api/types";
import TextInputPanel from "../components/TextInputPanel";
import ResultPanel from "../components/ResultPanel";
import SettingsPanel from "../components/SettingsPanel";
import TokenUsagePanel from "../components/TokenUsagePanel";

const DEFAULT_TEMP = 0.6;
const DEFAULT_MAX_TOKENS = 600;

export default function HomePage() {
  const [task, setTask] = useState<TaskType>("summarize");
  const [inputText, setInputText] = useState("");
  const [targetLanguage, setTargetLanguage] = useState("Spanish");
  const [temperature, setTemperature] = useState(DEFAULT_TEMP);
  const [maxTokens, setMaxTokens] = useState(DEFAULT_MAX_TOKENS);
  const [streaming, setStreaming] = useState(true);
  const [status, setStatus] = useState<"idle" | "streaming" | "error" | "done">(
    "idle"
  );
  const [output, setOutput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [meta, setMeta] = useState<AIResponse | null>(null);
  const [history, setHistory] = useState<UsageHistoryItem[]>([]);
  const [usageLoading, setUsageLoading] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const outputRef = useRef<string>("");

  const streamingSupported = useMemo(() => !!window.ReadableStream, []);

  useEffect(() => {
    refreshUsage();
  }, []);

  const buildRequest = (): AIRequest => ({
    task,
    input_text: inputText,
    target_language: task === "translate" ? targetLanguage : undefined,
    options: { temperature, max_tokens: maxTokens },
  });

  const refreshUsage = async () => {
    setUsageLoading(true);
    try {
      const items = await getRecentUsage();
      setHistory(items);
    } catch (e) {
      console.warn("Usage fetch failed", e);
    } finally {
      setUsageLoading(false);
    }
  };

  const handleSubmit = async () => {
    setError(null);
    setMeta(null);
    setOutput("");
    outputRef.current = "";

    if (!inputText.trim()) {
      setError("Input text is required.");
      return;
    }
    if (task === "translate" && !targetLanguage.trim()) {
      setError("Target language is required for translate.");
      return;
    }

    const request = buildRequest();

    if (streaming && streamingSupported) {
      abortRef.current?.abort();
      abortRef.current = new AbortController();
      setStatus("streaming");
      try {
        await streamAIRequest(
          request,
          (chunk) =>
            setOutput((prev: string) => {
              const next = prev + chunk;
              outputRef.current = next;
              return next;
            }),
          (data) => {
            setStatus("done");
            setMeta({
              id: data.id,
              task,
              model: data.model,
              input_text: inputText,
              output_text: outputRef.current,
              usage: {
                prompt_tokens: data.usage?.prompt_tokens || 0,
                completion_tokens: data.usage?.completion_tokens || 0,
                total_tokens: data.usage?.total_tokens || 0,
                estimated_cost: data.estimated_cost || 0,
              },
              created_at: new Date().toISOString(),
            });
            refreshUsage();
          },
          (msg) => {
            setStatus("error");
            setError(msg);
          },
          abortRef.current.signal
        );
      } catch (err: any) {
        if (err?.name === "AbortError") {
          setStatus("idle");
        } else {
          setStatus("error");
          setError(err?.message || "Streaming failed");
        }
      }
    } else {
      setStatus("streaming");
      try {
        const res = await sendAIRequest(request);
        setMeta(res);
        setOutput(res.output_text);
        setStatus("done");
        refreshUsage();
      } catch (err: any) {
        setStatus("error");
        setError(err?.message || "Request failed");
      }
    }
  };

  const handleStop = () => {
    abortRef.current?.abort();
    setStatus("idle");
  };

  return (
    <div className="page">
      <header className="nav">
        <h1>AI Content Generator</h1>
        <p className="muted">Summarize · Translate · Generate</p>
      </header>

      <main className="layout">
        <div className="left-col">
          <TextInputPanel
            task={task}
            setTask={setTask}
            inputText={inputText}
            setInputText={setInputText}
            targetLanguage={targetLanguage}
            setTargetLanguage={setTargetLanguage}
            temperature={temperature}
            setTemperature={setTemperature}
            maxTokens={maxTokens}
            setMaxTokens={setMaxTokens}
            onSubmit={handleSubmit}
            onClear={() => setInputText("")}
            streaming={streaming}
            setStreaming={setStreaming}
            streamingSupported={streamingSupported}
            disableSubmit={status === "streaming"}
          />
          <SettingsPanel
            modelHint="Backend model: configured server-side"
            streaming={streaming}
            setStreaming={setStreaming}
            streamingSupported={streamingSupported}
          />
        </div>

        <div className="right-col">
          <ResultPanel
            output={output}
            status={status}
            error={error}
            meta={meta}
            onStop={handleStop}
            isStreaming={status === "streaming"}
          />
          <TokenUsagePanel
            items={history}
            loading={usageLoading}
            onRefresh={refreshUsage}
          />
        </div>
      </main>
    </div>
  );
}
