'use client'

import { useState } from 'react'
import Onboarding from '@/components/Onboarding'
import ChatLayout from '@/components/ChatLayout'

export default function ChatPage() {
  const [started, setStarted] = useState(false)

  if (started) {
    return <ChatLayout />
  }

  return <Onboarding onStart={() => setStarted(true)} />
}
