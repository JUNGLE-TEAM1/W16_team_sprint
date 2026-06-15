import { AlertCircle } from "lucide-react";

type NoticeProps = {
  message: string | null;
};

export function Notice({ message }: NoticeProps) {
  if (!message) return null;

  return (
    <div className="notice" role="alert">
      <AlertCircle size={17} />
      <span>{message}</span>
    </div>
  );
}
