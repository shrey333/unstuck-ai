export interface Source {
  content: string;
  source: string;
}

export interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  isLoading?: boolean;
}
