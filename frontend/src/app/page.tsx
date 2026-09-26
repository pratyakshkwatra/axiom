"use client";
import React, { useState } from "react";
import dynamic from "next/dynamic";

const ChatInterface = dynamic(() => import("./ChatInterface"), { ssr: false });
const Settings = dynamic(() => import("./Settings"), { ssr: false });

export default function App() {
  const [view, setView] = useState<"chat" | "settings">("chat");

  return (
    <div className="flex h-screen bg-white text-[#334155] font-sans overflow-hidden selection:bg-[#2563EB]/20">
      <main className="flex-1 flex flex-col h-full relative w-full items-center justify-center">
         {view === "chat" ? (
           <ChatInterface onOpenSettings={() => setView("settings")} />
         ) : (
           <Settings onClose={() => setView("chat")} />
         )}
      </main>
    </div>
  );
}
