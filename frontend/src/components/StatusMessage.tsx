import type { StatusState } from "../types";

interface StatusMessageProps {
  status: StatusState;
}

export function StatusMessage({ status }: StatusMessageProps) {
  return (
    <div className={`status ${status.isError ? "is-error" : ""}`} role="status">
      <span className="status-dot" aria-hidden="true" />
      <span>{status.text}</span>
    </div>
  );
}
