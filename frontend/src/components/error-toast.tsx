'use client'

import React, { useEffect, useState } from 'react'

interface ErrorToastProps {
  message: string
  onClose: () => void
}

export function ErrorToast({ message, onClose }: ErrorToastProps) {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false)
      onClose()
    }, 5000)

    return () => clearTimeout(timer)
  }, [onClose])

  if (!isVisible) return null

  return (
    <div className="fixed bottom-4 right-4 bg-destructive text-destructive-foreground px-4 py-2 rounded-md shadow-lg">
      <div className="flex items-center gap-2">
        <span>{message}</span>
        <button
          onClick={() => {
            setIsVisible(false)
            onClose()
          }}
          className="ml-2 hover:opacity-80"
        >
          ✕
        </button>
      </div>
    </div>
  )
}
