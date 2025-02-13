import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import { Message } from "@/types/chat";
import { SourceReference } from "./source-reference";
import { Loader2, FileText } from "lucide-react";

interface ChatMessageProps {
  message: Message;
}

function FileUploadMessage({
  content,
  isLoading,
}: {
  content: string;
  isLoading?: boolean;
}) {
  const fileMatches = content.matchAll(/- (.+\.pdf) \((.+)\)/g);
  const files = Array.from(fileMatches).map((match) => ({
    name: match[1],
    size: match[2],
  }));

  return (
    <div
      className="space-y-2"
      role="status"
      aria-live="polite"
      aria-busy={isLoading}
    >
      <div className="flex items-center gap-2 text-sm">
        {isLoading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            <span className="font-medium">Uploading documents...</span>
          </>
        ) : (
          <>
            <span
              className="font-medium"
              aria-label="Documents uploaded successfully"
            >
              <span aria-hidden="true">📚</span> Documents uploaded
            </span>
          </>
        )}
      </div>
      {files.length > 0 && (
        <div
          className="flex flex-wrap gap-2"
          role="list"
          aria-label="Uploaded files"
        >
          {files.map((file, i) => (
            <div
              key={i}
              role="listitem"
              className="inline-flex items-center gap-2 px-3 py-1.5 bg-muted rounded-full text-sm"
            >
              <FileText
                className="h-4 w-4 shrink-0 text-muted-foreground"
                aria-hidden="true"
              />
              <span className="text-muted-foreground font-medium truncate max-w-[200px]">
                {file.name}
              </span>
              <span className="text-muted-foreground whitespace-nowrap">
                <span className="sr-only">File size:</span>
                {file.size}
              </span>
            </div>
          ))}
        </div>
      )}
      {isLoading && (
        <div className="sr-only" role="alert" aria-live="assertive">
          Uploading {files.length} document{files.length !== 1 ? "s" : ""}
        </div>
      )}
    </div>
  );
}

export function ChatMessage({ message }: ChatMessageProps) {
  // Handle file upload messages
  if (message.content?.includes("📚")) {
    return (
      <FileUploadMessage
        content={message.content}
        isLoading={message.isLoading}
      />
    );
  }

  // Handle general loading state
  if (message.isLoading) {
    return (
      <div className="flex items-center gap-2 text-muted-foreground">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span>Thinking...</span>
      </div>
    );
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
            code: ({ children }) => (
              <code className="px-1 py-0.5 bg-muted rounded text-sm font-mono">
                {children}
              </code>
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
