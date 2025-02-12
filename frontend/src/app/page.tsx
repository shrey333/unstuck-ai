"use client";

import { ChatInterface } from "@/components/chat-interface";
import { ErrorBoundary } from "@/components/error-boundary";

export default function Home() {
  return (
    <main className="min-h-screen">
      <ErrorBoundary>
        <ChatInterface />
      </ErrorBoundary>
    </main>
  );
}
