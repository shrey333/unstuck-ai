import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import { Message } from "@/types/chat";
import { SourceReference } from "./source-reference";

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  if (message.isLoading) {
    return <div className="animate-pulse">Thinking...</div>;
  }

  // Create a map of referenced sources
  const sourceMap = message.sources?.reduce((acc, source, index) => {
    acc[`${index + 1}`] = source;
    return acc;
  }, {} as Record<string, (typeof message.sources)[0]>);

  return (
    <div className="space-y-2">
      <div className="dark:prose-invert max-w-none">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeRaw]}
          components={{
            // Override default element styling
            p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
            ul: ({ children }) => (
              <ul className="list-disc pl-4 mb-2 last:mb-0">{children}</ul>
            ),
            ol: ({ children }) => (
              <ol className="list-decimal pl-4 mb-2 last:mb-0">{children}</ol>
            ),
            li: ({ children }) => (
              <li className="mb-1 last:mb-0">{children}</li>
            ),
            a: ({ href, children }) => (
              <a
                href={href}
                className="text-primary hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                {children}
              </a>
            ),
            code: ({ inline, children }) =>
              inline ? (
                <code className="px-1 py-0.5 bg-muted rounded text-sm font-mono">
                  {children}
                </code>
              ) : (
                <pre className="p-3 bg-muted rounded-lg overflow-x-auto">
                  <code className="text-sm font-mono">{children}</code>
                </pre>
              ),
            blockquote: ({ children }) => (
              <blockquote className="border-l-2 border-muted-foreground pl-4 italic">
                {children}
              </blockquote>
            ),
            h1: ({ children }) => (
              <h1 className="text-xl font-bold mb-2">{children}</h1>
            ),
            h2: ({ children }) => (
              <h2 className="text-lg font-bold mb-2">{children}</h2>
            ),
            h3: ({ children }) => (
              <h3 className="text-base font-bold mb-2">{children}</h3>
            ),
            // Handle span elements directly
            span: ({ id, children }) => {
              if (id && sourceMap?.[id]) {
                return (
                  <SourceReference key={id} id={id} source={sourceMap[id]} />
                );
              }
              return <span>{children}</span>;
            },
          }}
        >
          {message.content}
        </ReactMarkdown>
      </div>
    </div>
  );
}
