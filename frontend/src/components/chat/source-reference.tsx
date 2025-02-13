import React from "react";
import * as HoverCard from "@radix-ui/react-hover-card";
import { Source } from "@/types/chat";

interface SourceReferenceProps {
  id: string;
  source: Source;
}

function truncateText(text: string, maxLength: number = 200) {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trim() + "...";
}

export function SourceReference({ id, source }: SourceReferenceProps) {
  return (
    <HoverCard.Root>
      <HoverCard.Trigger asChild>
        <span
          id={id}
          className="inline-block text-primary cursor-help bg-blue-100 rounded-md px-2 hover:underline"
        >
          {id}
        </span>
      </HoverCard.Trigger>
      <HoverCard.Portal>
        <HoverCard.Content
          className="w-[320px] rounded-md bg-white dark:bg-zinc-900 p-4 shadow-lg border border-zinc-200 dark:border-zinc-800"
          sideOffset={5}
        >
          <div className="space-y-2">
            <div className="text-sm font-medium text-zinc-500 dark:text-zinc-400">
              {source.source}
            </div>
            <div className="text-sm text-zinc-700 dark:text-zinc-300">
              {truncateText(source.content)}
            </div>
          </div>
          <HoverCard.Arrow className="fill-white dark:fill-zinc-900" />
        </HoverCard.Content>
      </HoverCard.Portal>
    </HoverCard.Root>
  );
}
