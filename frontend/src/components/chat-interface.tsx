import React, { useState, useRef, useCallback } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Send, Plus } from "lucide-react";
import { useToast } from "./toast-provider";
import { Message } from "@/types/chat";
import { FileUpload } from "./chat/file-upload";
import { ChatMessage } from "./chat/message";
import { uploadFiles, askQuestion, APIError } from "@/lib/api";

// Format file size for display
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const { showToast } = useToast();

  // Handle starting a new chat
  const handleNewChat = useCallback(() => {
    // Clear messages
    setMessages([]);
    setInput("");
    
    // Clear chat_id cookie
    document.cookie = "chat_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    
    // Show toast notification
    showToast("Started a new chat", "success");
  }, [showToast]);

  // Simplified error handling
  const handleError = useCallback((error: unknown) => {
    console.error("Error:", error);

    // Handle common API errors
    if (error instanceof APIError) {
      const message = error.status === 413 ? "File too large. Please upload a smaller file."
        : error.status === 415 ? "Unsupported file type. Please upload a PDF file."
        : "Server error. Please try again.";
      showToast(message, "error");
      return;
    }

    // Handle network errors
    if (error instanceof TypeError && error.message === "Failed to fetch") {
      showToast("Network error: Please check your connection", "error");
      return;
    }

    // Default error message
    showToast("An error occurred. Please try again.", "error");
  }, [showToast]);

  // Handle file upload
  const handleFileUpload = useCallback(async (files: FileList) => {
    // Validate file types
    const invalidFiles = Array.from(files).filter(
      (file) => !file.type.includes("pdf")
    );
    if (invalidFiles.length > 0) {
      handleError(new Error("Only PDF files are supported"));
      return;
    }

    setIsLoading(true);

    try {
      await uploadFiles(files);

      // Create a nicely formatted message showing uploaded files
      const fileList = Array.from(files)
        .map((file) => `- ${file.name} (${formatFileSize(file.size)})`)
        .join("\n");

      const uploadMessage = `📚 Uploaded ${files.length} document${
        files.length > 1 ? "s" : ""
      }:\n${fileList}`;

      setMessages((prev) => [
        ...prev,
        {
          role: "user",
          content: uploadMessage,
        },
      ]);
    } catch (error) {
      handleError(error);
    } finally {
      setIsLoading(false);
    }
  }, [handleError]);

  // Handle form submission
  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!input.trim() || isLoading) return;

      const question = input.trim();
      setInput("");
      
      // Add user message immediately without loading state
      setMessages((prev) => [...prev, { role: "user", content: question }]);
      setIsLoading(true);

      try {
        // Add assistant message with loading state
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "",
            isLoading: true,
          },
        ]);

        const data = await askQuestion(question);

        // Update the last message with the response data
        setMessages((prev) => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1] = {
            role: "assistant",
            content: data.answer,
            sources: data.source,
            isLoading: false,
          };
          return newMessages;
        });
      } catch (error) {
        // Remove the loading message and show error
        setMessages((prev) => prev.slice(0, -1));
        handleError(error);
      } finally {
        setIsLoading(false);
      }
    },
    [input, isLoading, handleError]
  );

  // Scroll to bottom when messages change
  React.useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto">
      <div className="flex justify-between items-center p-4 border-b">
        <h1 className="text-lg font-semibold">Chat with Documents</h1>
        <Button
          variant="outline"
          size="sm"
          onClick={handleNewChat}
          disabled={isLoading}
          className="gap-2"
        >
          <Plus className="h-4 w-4" />
          New Chat
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
            <p className="mb-2">Upload a document to get started</p>
            <p>or ask a question about previously uploaded documents</p>
          </div>
        ) : (
          <div className="space-y-6">
            {messages.map((message, i) => (
              <div
                key={i}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-4 ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  }`}
                >
                  <ChatMessage message={message} />
                </div>
              </div>
            ))}
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      <div className="border-t bg-background p-4">
        <form onSubmit={handleSubmit} className="flex items-center gap-2">
          <FileUpload onUpload={handleFileUpload} isLoading={isLoading} />
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button
            type="submit"
            size="icon"
            disabled={isLoading || !input.trim()}
          >
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}
