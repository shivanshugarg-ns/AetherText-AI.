import React from "react";
import { UsageHistoryItem } from "../api/types";

interface Props {
  items: UsageHistoryItem[];
  loading: boolean;
  onRefresh: () => void;
}

export default function TokenUsagePanel({ items, loading, onRefresh }: Props) {
  return (
    <div className="panel">
      <div className="section-head">
        <h3>Recent Usage</h3>
        <button className="mini" type="button" onClick={onRefresh} disabled={loading}>
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>
      <div className="table">
        <div className="table-head">
          <span>Time</span>
          <span>Task</span>
          <span>Tokens</span>
          <span>Cost</span>
        </div>
        {items.length === 0 && <p className="muted">No usage yet.</p>}
        {items.map((item) => (
          <div className="table-row" key={item.id}>
            <span>{new Date(item.created_at).toLocaleTimeString()}</span>
            <span>{item.task}</span>
            <span>
              {item.prompt_tokens}p / {item.completion_tokens}c
            </span>
            <span>${item.estimated_cost.toFixed(6)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
