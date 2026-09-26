"use client";
import React, { useState, useEffect, useRef } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import KnowledgeGraph from "./KnowledgeGraph";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const markdownComponents = {
  h1: (props: any) => <h1 className="text-xl font-semibold text-[#18181B] mt-4 mb-2" {...props} />,
  h2: (props: any) => <h2 className="text-lg font-semibold text-[#18181B] mt-4 mb-2" {...props} />,
  h3: (props: any) => <h3 className="text-base font-semibold text-[#18181B] mt-3 mb-1" {...props} />,
  p: (props: any) => <p className="mb-3 last:mb-0" {...props} />,
  ul: (props: any) => <ul className="list-disc pl-6 mb-3 space-y-1" {...props} />,
  ol: (props: any) => <ol className="list-decimal pl-6 mb-3 space-y-1" {...props} />,
  li: (props: any) => <li className="leading-7" {...props} />,
  strong: (props: any) => <strong className="font-semibold text-[#18181B]" {...props} />,
  a: (props: any) => <a className="text-[#3B82F6] underline" target="_blank" rel="noreferrer" {...props} />,
  code: (props: any) => <code className="bg-[#F4F4F5] rounded px-1.5 py-0.5 text-[14px] font-mono" {...props} />,
  pre: (props: any) => <pre className="bg-[#F4F4F5] rounded-xl p-4 mb-3 overflow-x-auto text-[14px]" {...props} />,
  blockquote: (props: any) => <blockquote className="border-l-4 border-[#E4E4E7] pl-4 text-[#71717A] mb-3" {...props} />,
  hr: () => <hr className="my-4 border-[#E4E4E7]" />,
  table: (props: any) => <div className="overflow-x-auto mb-3"><table className="w-full text-sm border border-[#E4E4E7] rounded-lg" {...props} /></div>,
  th: (props: any) => <th className="text-left font-semibold text-[#18181B] bg-[#FAFAFA] border-b border-[#E4E4E7] px-3 py-2" {...props} />,
  td: (props: any) => <td className="border-b border-[#F4F4F5] px-3 py-2" {...props} />,
};

export default function ChatInterface({ onOpenSettings }: { onOpenSettings?: () => void }) {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [progressStep, setProgressStep] = useState<string>("");
  const [userRole, setUserRole] = useState("ENGINEER");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, progressStep]);

  const handleSend = async (overrideInput?: string) => {
    const textToSend = overrideInput || input;
    if (!textToSend.trim()) return;
    
    const userMsg = { role: "user", content: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);
    
    const steps = [
      "Understanding Request...",
      "Checking Permissions...",
      "Searching Enterprise Memory...",
      "Connecting Context...",
      "Building Answer..."
    ];
    
    for (const step of steps) {
      setProgressStep(step);
      await new Promise(r => setTimeout(r, 400));
    }

    try {
      const res = await fetch("http://localhost:8000/api/memory/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: textToSend, organization_id: "org-1", user_role: userRole })
      });
      const data = await res.json();
      
      setMessages((prev) => [...prev, { 
        role: "assistant", 
        content: data.answer, 
        chartData: data.chartData, 
        uiComponent: data.uiComponent,
        suggestions: data.suggestions,
        isNew: true
      }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "assistant", content: "Error connecting to AXIOM backend.", isNew: true }]);
    } finally {
      setIsLoading(false);
      setProgressStep("");
    }
  };

  const startListening = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert("Speech recognition is not supported in this browser.");
      return;
    }
    
    // @ts-ignore
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = true;
    
    recognition.onstart = () => setIsListening(true);
    
    recognition.onresult = (event: any) => {
      const transcript = Array.from(event.results)
        .map((result: any) => result[0].transcript)
        .join('');
      setInput(transcript);
    };
    
    recognition.onerror = (event: any) => {
      console.error("Speech recognition error", event.error);
      setIsListening(false);
    };
    
    recognition.onend = () => {
      setIsListening(false);
    };
    
    recognition.start();
  };

  return (
    <div className="flex flex-col h-full w-full bg-[#FAFAFA] relative font-sans text-[#18181B] selection:bg-[#3B82F6]/20">
      {/* HEADER */}
      <header className="flex-shrink-0 flex items-center justify-between px-8 py-5 bg-white sticky top-0 z-50 border-b border-[#E4E4E7]/50 shadow-[0_1px_2px_rgba(0,0,0,0.02)] transition-all duration-300">
         <div className="flex items-center gap-4">
           <h2 className="text-xl font-black tracking-tighter text-[#18181B]">AXIOM</h2>
           <div className="h-4 w-[1px] bg-[#E4E4E7] mx-1"></div>
           <span className="flex items-center gap-2 text-[10px] uppercase font-bold tracking-widest text-[#71717A]">
             <span className="w-1.5 h-1.5 rounded-full bg-[#10B981]"></span>
             System Operational
           </span>
         </div>
         <button onClick={onOpenSettings} className="group flex items-center gap-2 text-sm font-medium text-[#71717A] hover:text-[#18181B] transition-colors">
            Settings
         </button>
      </header>

      {/* CONVERSATION AREA */}
      <div className="flex-1 overflow-y-auto px-6 py-10 scroll-smooth">
        <div className="w-full max-w-[800px] mx-auto pb-48">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center text-center mt-[8vh] animate-in fade-in zoom-in-95 duration-700 ease-out">
              
              {/* AXIOM CORE Visual */}
              <div className="relative w-64 h-64 mb-8 flex items-center justify-center">
                <svg viewBox="0 0 200 200" className="w-full h-full text-[#E4E4E7] animate-[spin_60s_linear_infinite]">
                  <circle cx="100" cy="100" r="80" fill="none" stroke="currentColor" strokeWidth="0.5" strokeDasharray="2 4" />
                  <circle cx="100" cy="100" r="50" fill="none" stroke="currentColor" strokeWidth="0.5" strokeDasharray="4 4" />
                  
                  {/* Nodes */}
                  <circle cx="100" cy="20" r="3" fill="#18181B" />
                  <circle cx="170" cy="60" r="2" fill="#71717A" />
                  <circle cx="180" cy="140" r="2" fill="#71717A" />
                  <circle cx="100" cy="180" r="3" fill="#3B82F6" className="animate-pulse" />
                  <circle cx="20" cy="140" r="2" fill="#71717A" />
                  <circle cx="30" cy="60" r="2" fill="#71717A" />
                  
                  {/* Inner Nodes */}
                  <circle cx="100" cy="50" r="1.5" fill="#18181B" />
                  <circle cx="140" cy="80" r="1.5" fill="#71717A" />
                  <circle cx="130" cy="130" r="1.5" fill="#71717A" />
                  <circle cx="70" cy="130" r="1.5" fill="#71717A" />
                  <circle cx="60" cy="80" r="1.5" fill="#71717A" />

                  {/* Lines */}
                  <line x1="100" y1="20" x2="100" y2="50" stroke="currentColor" strokeWidth="0.5" />
                  <line x1="170" y1="60" x2="140" y2="80" stroke="currentColor" strokeWidth="0.5" />
                  <line x1="100" y1="180" x2="130" y2="130" stroke="#3B82F6" strokeWidth="0.5" className="opacity-50" />
                  <line x1="20" y1="140" x2="70" y2="130" stroke="currentColor" strokeWidth="0.5" />
                  <line x1="100" y1="180" x2="70" y2="130" stroke="currentColor" strokeWidth="0.5" />
                  
                  {/* Center Hub */}
                  <circle cx="100" cy="100" r="4" fill="#18181B" />
                  <line x1="100" y1="100" x2="100" y2="50" stroke="currentColor" strokeWidth="0.5" />
                  <line x1="100" y1="100" x2="140" y2="80" stroke="currentColor" strokeWidth="0.5" />
                  <line x1="100" y1="100" x2="130" y2="130" stroke="currentColor" strokeWidth="0.5" />
                  <line x1="100" y1="100" x2="70" y2="130" stroke="currentColor" strokeWidth="0.5" />
                  <line x1="100" y1="100" x2="60" y2="80" stroke="currentColor" strokeWidth="0.5" />
                </svg>
              </div>

              <h1 className="text-4xl font-bold tracking-tight text-[#18181B] mb-3">AXIOM</h1>
              <p className="text-xl text-[#3F3F46] mb-3 font-medium">Your enterprise, connected.</p>
              <p className="text-sm text-[#71717A] max-w-lg mb-8">Memory, context, permissions and actions — through one interface.</p>
              
              <div className="flex items-center gap-4 text-[11px] font-medium text-[#A1A1AA] uppercase tracking-widest mb-10">
                <span>12,482 memories</span>
                <span>·</span>
                <span>8 connected sources</span>
                <span>·</span>
                <span>24 agents</span>
                <span>·</span>
                <span>31 policies</span>
              </div>

              <div className="flex items-center gap-6 text-xs font-semibold text-[#71717A] mb-12">
                <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-[#E4E4E7]"></span> Memory</span>
                <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-[#E4E4E7]"></span> Context</span>
                <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-[#3B82F6]"></span> Policy</span>
                <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-[#E4E4E7]"></span> Agents</span>
                <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-[#E4E4E7]"></span> Actions</span>
              </div>
              
              <div className="w-full flex flex-wrap justify-center gap-3">
                {[
                  "Show me the context around Project Atlas",
                  "Why is the Acme escalation still unresolved?",
                  "Create a support agent",
                  "Show me who can access customer data",
                ].map((suggestion, i) => (
                  <button 
                    key={i}
                    onClick={() => handleSend(suggestion)} 
                    className="group bg-white border border-[#E4E4E7] hover:border-[#3F3F46] rounded-full px-5 py-2.5 text-xs font-medium text-[#71717A] hover:text-[#18181B] transition-colors"
                  >
                    "{suggestion}"
                  </button>
                ))}
              </div>
            </div>
          )}
          
          <div className="space-y-10">
            {messages.map((msg, i) => (
              <div key={i} className={`flex gap-5 animate-in fade-in slide-in-from-bottom-4 duration-500 ease-out ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                
                {msg.role !== 'user' && (
                  <div className="w-9 h-9 flex-shrink-0 mt-1">
                    <div className="w-full h-full rounded-full bg-gradient-to-tr from-[#18181B] to-[#3F3F46] text-white flex items-center justify-center shadow-md">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2L2 22H22L12 2Z" fill="white"/></svg>
                    </div>
                  </div>
                )}
                
                <div className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} max-w-[85%]`}>
                  
                  {msg.role === 'user' ? (
                    <div className="px-6 py-3.5 bg-[#18181B] text-white text-[15px] leading-relaxed rounded-2xl rounded-tr-sm shadow-md font-medium">
                      {msg.content}
                    </div>
                  ) : (
                    <div className="text-[16px] leading-8 text-[#3F3F46] pt-1">
                      <StreamedText text={msg.content} isNew={msg.isNew} />
                    </div>
                  )}
                  
                  {msg.chartData && msg.chartData.length > 0 && (
                    <div className="mt-8 p-6 bg-white rounded-2xl border border-[#E4E4E7] shadow-sm animate-in fade-in zoom-in-95 duration-500 delay-200 fill-mode-both w-full min-w-[500px]">
                      <h4 className="text-sm font-bold text-[#18181B] mb-6 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-[#3B82F6]"></span> Analytics
                      </h4>
                      <div className="h-64 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={msg.chartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#F4F4F5" vertical={false} />
                            <XAxis dataKey="name" stroke="#A1A1AA" fontSize={12} tickLine={false} axisLine={false} />
                            <YAxis stroke="#A1A1AA" fontSize={12} tickLine={false} axisLine={false} />
                            <Tooltip cursor={{ fill: '#F4F4F5' }} contentStyle={{ backgroundColor: '#18181B', borderColor: '#27272A', borderRadius: '8px', color: '#FFFFFF', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }} />
                            <Bar dataKey="value" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  )}
                  
                  {msg.uiComponent === 'agent_configuration' && <AgentConfiguration />}
                  {msg.uiComponent === 'policy_preview' && <PolicyPreview />}
                  {msg.uiComponent === 'context_view' && <ContextualView />}
                  {msg.uiComponent === 'action_confirmation' && <ActionConfirmation />}
                  {msg.uiComponent === 'audit_timeline' && <AuditTimeline />}
                  {msg.uiComponent === 'permission_check' && <PermissionCheck />}
                  {msg.uiComponent === 'knowledge_graph' && (
                    <div className="mt-8 border border-[#E4E4E7] rounded-2xl bg-white overflow-hidden shadow-sm animate-in fade-in zoom-in-95 duration-500 delay-300 min-w-[600px] h-[500px]">
                      <KnowledgeGraph />
                    </div>
                  )}
                  
                  {/* Suggestions (only show for the latest message if it has them) */}
                  {msg.suggestions && msg.suggestions.length > 0 && i === messages.length - 1 && !isLoading && (
                    <div className="mt-6 flex flex-wrap gap-2 animate-in fade-in slide-in-from-bottom-2 duration-500 delay-500 fill-mode-both">
                      {msg.suggestions.map((suggestion: string, idx: number) => (
                        <button
                          key={idx}
                          onClick={() => handleSend(suggestion)}
                          className="px-4 py-2 bg-white border border-[#E4E4E7] hover:border-[#3B82F6] hover:bg-[#EFF6FF] text-[#3F3F46] hover:text-[#3B82F6] text-sm font-medium rounded-full shadow-sm transition-all duration-300"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {isLoading && progressStep && (
              <div className="flex flex-col gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300 max-w-[85%]">
                <div className="text-[11px] font-bold text-[#71717A] flex flex-col gap-2">
                  <div className={`flex items-center gap-2 ${progressStep === 'Understanding Request...' || progressStep === 'Checking Permissions...' || progressStep === 'Searching Enterprise Memory...' || progressStep === 'Connecting Context...' || progressStep === 'Building Answer...' ? 'text-[#18181B]' : 'text-[#A1A1AA]'}`}>
                    <span className="w-1.5 h-1.5 rounded-full bg-current"></span> UNDERSTANDING REQUEST
                  </div>
                  <div className={`flex items-center gap-2 ${progressStep === 'Checking Permissions...' || progressStep === 'Searching Enterprise Memory...' || progressStep === 'Connecting Context...' || progressStep === 'Building Answer...' ? 'text-[#18181B]' : 'text-[#A1A1AA]'}`}>
                    <span className="w-1.5 h-1.5 rounded-full bg-current"></span> CHECKING PERMISSIONS
                  </div>
                  <div className={`flex items-center gap-2 ${progressStep === 'Searching Enterprise Memory...' || progressStep === 'Connecting Context...' || progressStep === 'Building Answer...' ? 'text-[#18181B]' : 'text-[#A1A1AA]'}`}>
                    <span className="w-1.5 h-1.5 rounded-full bg-current"></span> SEARCHING ENTERPRISE MEMORY
                  </div>
                  <div className={`flex items-center gap-2 ${progressStep === 'Connecting Context...' || progressStep === 'Building Answer...' ? 'text-[#18181B]' : 'text-[#A1A1AA]'}`}>
                    <span className="w-1.5 h-1.5 rounded-full bg-current"></span> CONNECTING RELATED CONTEXT
                  </div>
                  <div className={`flex items-center gap-2 ${progressStep === 'Building Answer...' ? 'text-[#18181B] animate-pulse' : 'text-[#A1A1AA]'}`}>
                    <span className="w-1.5 h-1.5 rounded-full bg-current"></span> BUILDING ANSWER
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} className="h-4" />
          </div>
        </div>
      </div>
      
      {/* INPUT AREA */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-[#FAFAFA] via-[#FAFAFA] to-transparent pt-24 pb-8 px-6 flex justify-center z-20 pointer-events-none">
        <div className="w-full max-w-[700px] relative pointer-events-auto flex flex-col items-center">
          <div className="w-full flex items-center gap-2 mb-3 text-xs font-medium text-[#71717A]">
            <span>Signed in as</span>
            {[
              { id: "ENGINEER", label: "Engineer" },
              { id: "SUPPORT_AGENT", label: "Support Agent" },
              { id: "CONTRACTOR", label: "Contractor" },
              { id: "HR_ADMIN", label: "HR Admin" },
            ].map((r) => (
              <button
                key={r.id}
                onClick={() => setUserRole(r.id)}
                className={`rounded-full px-3 py-1 border transition-colors ${userRole === r.id ? 'bg-[#18181B] border-[#18181B] text-white' : 'bg-white border-[#E4E4E7] hover:border-[#3F3F46] hover:text-[#18181B]'}`}
              >
                {r.label}
              </button>
            ))}
          </div>
          <div className="w-full relative flex items-center bg-white border border-[#E4E4E7] shadow-sm rounded-2xl overflow-hidden transition-all duration-300 focus-within:border-[#71717A] focus-within:shadow-md">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask AXIOM anything..."
              className="w-full bg-transparent pl-5 pr-24 py-4 text-[15px] font-medium text-[#18181B] placeholder-[#A1A1AA] focus:outline-none"
            />
            <div className="absolute right-2 flex items-center gap-1.5">
              <button 
                onClick={startListening}
                className={`h-9 w-9 flex items-center justify-center rounded-xl transition-all ${isListening ? 'text-[#EF4444] bg-[#FEF2F2] animate-pulse' : 'text-[#71717A] hover:text-[#18181B] hover:bg-[#F4F4F5]'}`}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="22"></line></svg>
              </button>
              <button 
                onClick={() => handleSend()}
                disabled={isLoading || !input.trim()}
                className="h-9 w-9 flex items-center justify-center bg-[#18181B] hover:bg-[#3F3F46] disabled:bg-[#F4F4F5] disabled:text-[#A1A1AA] text-white rounded-xl transition-colors duration-300"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
              </button>
            </div>
          </div>
          <p className="text-[11px] font-medium text-[#A1A1AA] mt-3 tracking-wide">Ask about your enterprise, configure an agent, manage access, or take action.</p>
        </div>
      </div>
    </div>
  );
}

// Simulated streaming text component
function StreamedText({ text, isNew }: { text: string, isNew?: boolean }) {
  const [displayedText, setDisplayedText] = useState(isNew ? "" : text);
  
  useEffect(() => {
    if (!isNew) return;
    
    let currentIndex = 0;
    const interval = setInterval(() => {
      currentIndex += 6;
      setDisplayedText(text.slice(0, currentIndex));
      if (currentIndex >= text.length) {
        clearInterval(interval);
      }
    }, 15);
    
    return () => clearInterval(interval);
  }, [text, isNew]);

  return <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>{displayedText}</ReactMarkdown>;
}

// ==========================================
// DYNAMIC UI COMPONENTS
// ==========================================

function AgentConfiguration() {
  const [showAdvanced, setShowAdvanced] = useState(false);

  return (
    <div className="mt-8 border border-[#E4E4E7] rounded-2xl bg-white overflow-hidden shadow-sm animate-in fade-in zoom-in-95 duration-500 delay-300 fill-mode-both min-w-[500px]">
      <div className="px-6 py-5 border-b border-[#E4E4E7] flex items-center justify-between">
        <h3 className="font-bold text-[#18181B] flex items-center gap-2">
          <span className="w-8 h-8 rounded-full bg-[#EFF6FF] text-[#3B82F6] flex items-center justify-center">🤖</span>
          Create AI Agent
        </h3>
        <button onClick={() => setShowAdvanced(!showAdvanced)} className="text-xs font-bold text-[#71717A] hover:text-[#18181B] flex items-center gap-1 transition-colors">
          {showAdvanced ? "Hide Detailed" : "View Detailed"} <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={`transition-transform duration-300 ${showAdvanced ? 'rotate-180' : ''}`}><polyline points="6 9 12 15 18 9"></polyline></svg>
        </button>
      </div>
      <div className="p-6 space-y-6">
        <div>
          <label className="block text-[11px] font-bold text-[#71717A] uppercase tracking-wider mb-2">Agent Name</label>
          <input type="text" defaultValue="Support Agent" className="w-full bg-[#FAFAFA] border border-[#E4E4E7] rounded-xl px-4 py-3 text-[15px] font-medium text-[#18181B] focus:outline-none focus:border-[#3B82F6] focus:bg-white transition-all shadow-inner" />
        </div>
        
        <div>
          <label className="block text-[11px] font-bold text-[#71717A] uppercase tracking-wider mb-2">Data Access</label>
          <div className="space-y-0 border border-[#E4E4E7] rounded-xl overflow-hidden divide-y divide-[#E4E4E7]">
            <label className="flex items-center justify-between p-4 cursor-pointer hover:bg-[#FAFAFA] transition-colors">
              <span className="text-[15px] font-medium text-[#18181B] flex items-center gap-3"><span className="text-xl">📞</span> Freshservice</span>
              <input type="checkbox" defaultChecked className="accent-[#3B82F6] w-5 h-5 cursor-pointer" /> 
            </label>
            <label className="flex items-center justify-between p-4 cursor-pointer hover:bg-[#FAFAFA] transition-colors">
              <span className="text-[15px] font-medium text-[#18181B] flex items-center gap-3"><span className="text-xl">💬</span> Slack</span>
              <input type="checkbox" defaultChecked className="accent-[#3B82F6] w-5 h-5 cursor-pointer" /> 
            </label>
          </div>
        </div>

        {showAdvanced && (
          <div className="pt-4 border-t border-[#E4E4E7] space-y-6 animate-in fade-in slide-in-from-top-4 duration-300">
            <div>
              <label className="block text-[11px] font-bold text-[#71717A] uppercase tracking-wider mb-2">Inference Model</label>
              <select className="w-full bg-white border border-[#E4E4E7] rounded-xl px-4 py-3 text-[15px] font-medium text-[#18181B] focus:outline-none focus:border-[#3B82F6]">
                <option>Claude 3.5 Sonnet (Default)</option>
                <option>Claude 3 Opus (High Reasoning)</option>
                <option>GPT-4o</option>
              </select>
            </div>
            <div>
              <label className="block text-[11px] font-bold text-[#71717A] uppercase tracking-wider mb-2">Rate Limiting</label>
              <div className="flex items-center gap-4">
                 <input type="range" min="1" max="100" defaultValue="50" className="w-full accent-[#3B82F6]" />
                 <span className="text-sm font-bold text-[#18181B]">50 req/min</span>
              </div>
            </div>
            <div>
              <label className="block text-[11px] font-bold text-[#71717A] uppercase tracking-wider mb-2">Fallback Behavior</label>
              <label className="flex items-center gap-3"><input type="checkbox" defaultChecked className="accent-[#3B82F6] w-4 h-4" /> <span className="text-sm font-medium text-[#3F3F46]">Halt and alert admin on unhandled exception</span></label>
            </div>
          </div>
        )}
      </div>
      <div className="px-6 py-4 border-t border-[#E4E4E7] bg-[#FAFAFA] flex justify-end">
        <button className="bg-[#18181B] hover:bg-[#3B82F6] text-white px-6 py-2.5 rounded-xl text-[15px] font-semibold shadow-md transition-colors duration-300">
          Deploy Agent
        </button>
      </div>
    </div>
  );
}

function PolicyPreview() {
  const [showAdvanced, setShowAdvanced] = useState(false);

  return (
    <div className="mt-8 border border-[#E4E4E7] rounded-2xl bg-white overflow-hidden shadow-sm animate-in fade-in zoom-in-95 duration-500 delay-300 fill-mode-both min-w-[500px]">
      <div className="px-6 py-5 border-b border-[#E4E4E7] flex justify-between items-center bg-[#FAFAFA]">
        <h3 className="font-bold text-[#18181B] flex items-center gap-2">
          <span className="w-8 h-8 rounded-full bg-[#F3F4F6] flex items-center justify-center">🛡️</span>
          Access Policy Draft
        </h3>
        <div className="flex items-center gap-3">
          <span className="text-xs font-bold bg-[#E4E4E7] text-[#71717A] px-2 py-1 rounded">RBAC</span>
          <button onClick={() => setShowAdvanced(!showAdvanced)} className="text-xs font-bold text-[#71717A] hover:text-[#18181B] flex items-center gap-1 transition-colors">
            {showAdvanced ? "Hide Detailed" : "View Detailed"} <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={`transition-transform duration-300 ${showAdvanced ? 'rotate-180' : ''}`}><polyline points="6 9 12 15 18 9"></polyline></svg>
          </button>
        </div>
      </div>
      <div className="p-0">
        <div className="p-6 border-b border-[#E4E4E7]">
          <h4 className="text-[11px] font-bold text-[#059669] uppercase tracking-widest mb-3 flex items-center gap-2">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            ALLOW
          </h4>
          <p className="font-bold text-[#18181B] text-[16px] mb-3">Engineering Managers</p>
          <ul className="text-[15px] text-[#3F3F46] space-y-2">
            <li className="flex items-center gap-3"><span className="text-[#A1A1AA]">→</span> Read project information</li>
            <li className="flex items-center gap-3"><span className="text-[#A1A1AA]">→</span> Only projects belonging to their teams</li>
          </ul>
        </div>
        <div className="p-6 bg-[#FEF2F2]/30">
          <h4 className="text-[11px] font-bold text-[#DC2626] uppercase tracking-widest mb-3 flex items-center gap-2">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            DENY
          </h4>
          <ul className="text-[15px] text-[#3F3F46] space-y-2">
            <li className="flex items-center gap-3"><span className="text-[#A1A1AA]">→</span> HR records</li>
          </ul>
        </div>
        
        {showAdvanced && (
          <div className="p-6 border-t border-[#E4E4E7] bg-[#FAFAFA] space-y-6 animate-in fade-in slide-in-from-top-4 duration-300">
            <div>
              <label className="block text-[11px] font-bold text-[#71717A] uppercase tracking-wider mb-2">Priority Weight</label>
              <input type="number" defaultValue="100" className="w-full bg-white border border-[#E4E4E7] rounded-xl px-4 py-2 text-[15px] font-medium text-[#18181B] focus:outline-none focus:border-[#3B82F6]" />
            </div>
            <div>
              <label className="block text-[11px] font-bold text-[#71717A] uppercase tracking-wider mb-2">IAM JSON Output (Auto-Generated)</label>
              <pre className="text-[11px] bg-[#18181B] text-[#A1A1AA] p-4 rounded-xl overflow-x-auto border border-[#3F3F46]">
{`{
  "Version": "2024-10-12",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["axiom:ReadProject"],
      "Resource": ["arn:axiom:project:team:manager/*"]
    }
  ]
}`}
              </pre>
            </div>
          </div>
        )}
      </div>
      <div className="px-6 py-4 border-t border-[#E4E4E7] flex justify-between bg-white">
        <button className="text-[#3F3F46] hover:text-[#18181B] px-5 py-2.5 rounded-xl text-[15px] font-semibold border border-[#E4E4E7] hover:bg-[#FAFAFA] transition-colors">
          Test Policy
        </button>
        <button className="bg-[#18181B] hover:bg-[#3B82F6] text-white px-6 py-2.5 rounded-xl text-[15px] font-semibold shadow-md transition-colors duration-300">
          Enforce Policy
        </button>
      </div>
    </div>
  );
}

function ContextualView() {
  const [showAdvanced, setShowAdvanced] = useState(false);

  return (
    <div className="mt-8 border border-[#E4E4E7] rounded-2xl bg-white overflow-hidden shadow-sm animate-in fade-in zoom-in-95 duration-500 delay-300 fill-mode-both min-w-[500px]">
      <div className="px-6 py-5 border-b border-[#E4E4E7] flex justify-between items-center bg-gradient-to-r from-white to-[#FAFAFA]">
        <h3 className="font-bold text-[#18181B] text-lg flex items-center gap-3">
          <span className="w-8 h-8 rounded-full bg-[#F3F4F6] flex items-center justify-center text-base">📁</span>
          Project Atlas
        </h3>
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#EFF6FF] text-[#2563EB] text-xs font-bold border border-[#BFDBFE]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#3B82F6] animate-pulse"></span> IN PROGRESS
          </span>
          <button onClick={() => setShowAdvanced(!showAdvanced)} className="text-xs font-bold text-[#71717A] hover:text-[#18181B] flex items-center gap-1 transition-colors">
            {showAdvanced ? "Hide Detailed" : "View Detailed"} <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={`transition-transform duration-300 ${showAdvanced ? 'rotate-180' : ''}`}><polyline points="6 9 12 15 18 9"></polyline></svg>
          </button>
        </div>
      </div>
      <div className="p-6">
        <div className="grid grid-cols-2 gap-y-8 gap-x-6">
          <div className="bg-[#FAFAFA] p-4 rounded-xl border border-[#E4E4E7]/50">
            <h4 className="text-[11px] font-bold text-[#71717A] uppercase tracking-widest mb-1">People</h4>
            <p className="text-xl text-[#18181B] font-bold">4 <span className="text-sm font-medium text-[#71717A]">relevant</span></p>
          </div>
          <div className="bg-[#FAFAFA] p-4 rounded-xl border border-[#E4E4E7]/50">
            <h4 className="text-[11px] font-bold text-[#71717A] uppercase tracking-widest mb-1">Decisions</h4>
            <p className="text-xl text-[#18181B] font-bold">7</p>
          </div>
          <div className="bg-[#FAFAFA] p-4 rounded-xl border border-[#E4E4E7]/50">
            <h4 className="text-[11px] font-bold text-[#71717A] uppercase tracking-widest mb-1">Issues</h4>
            <p className="text-xl text-[#18181B] font-bold">12 <span className="text-sm font-medium text-[#DC2626]">3 open</span></p>
          </div>
          <div className="bg-[#FAFAFA] p-4 rounded-xl border border-[#E4E4E7]/50">
            <h4 className="text-[11px] font-bold text-[#71717A] uppercase tracking-widest mb-1">Meetings</h4>
            <p className="text-xl text-[#18181B] font-bold">9</p>
          </div>
        </div>
        
        {showAdvanced && (
          <div className="mt-6 pt-6 border-t border-[#E4E4E7] space-y-4 animate-in fade-in slide-in-from-top-4 duration-300">
            <div>
              <h4 className="text-[11px] font-bold text-[#71717A] uppercase tracking-widest mb-2">Data Sources</h4>
              <ul className="text-sm text-[#3F3F46] space-y-1">
                <li>• Jira Project: ATLAS (98% match)</li>
                <li>• Slack Channel: #prj-atlas-core (95% match)</li>
                <li>• Google Drive: "Atlas Q3 Spec" (91% match)</li>
              </ul>
            </div>
            <div>
              <h4 className="text-[11px] font-bold text-[#71717A] uppercase tracking-widest mb-2">Vector Proximity Matrix</h4>
              <p className="text-xs font-mono text-[#71717A] bg-[#FAFAFA] p-3 border border-[#E4E4E7] rounded-lg">
                [0.912, 0.443, -0.102, 0.887, ...]<br/>
                Nearest neighbor: "Project Titan" (0.84 cosine dist)
              </p>
            </div>
          </div>
        )}
      </div>
      <div className="px-6 py-4 border-t border-[#E4E4E7] bg-[#FAFAFA]">
        <p className="text-[13px] text-[#71717A] font-medium flex items-center gap-2">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
          Ask: "Why was the architecture changed?"
        </p>
      </div>
    </div>
  );
}

function ActionConfirmation() {
  const [showAdvanced, setShowAdvanced] = useState(false);

  return (
    <div className="mt-8 border border-[#FDE68A] rounded-2xl bg-white overflow-hidden shadow-lg animate-in fade-in zoom-in-95 duration-500 delay-300 fill-mode-both min-w-[500px]">
      <div className="px-6 py-5 border-b border-[#FDE68A] bg-[#FFFBEB] flex items-center justify-between">
        <h3 className="font-bold text-[#B45309] flex items-center gap-2">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
          Action Confirmation
        </h3>
        <button onClick={() => setShowAdvanced(!showAdvanced)} className="text-xs font-bold text-[#B45309] hover:text-[#92400E] flex items-center gap-1 transition-colors">
          {showAdvanced ? "Hide Detailed" : "View Detailed"} <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={`transition-transform duration-300 ${showAdvanced ? 'rotate-180' : ''}`}><polyline points="6 9 12 15 18 9"></polyline></svg>
        </button>
      </div>
      <div className="p-6">
        <p className="text-[15px] font-semibold text-[#18181B] mb-5">AXIOM is about to perform an external action on your behalf.</p>
        
        <div className="bg-[#FAFAFA] border border-[#E4E4E7] rounded-xl p-5 shadow-inner">
          <p className="text-[11px] font-bold text-[#71717A] uppercase tracking-widest mb-3">Target: Slack (#engineering)</p>
          <div className="pl-4 border-l-2 border-[#3B82F6]">
             <p className="text-[15px] text-[#3F3F46] font-medium leading-relaxed">"Deployment has been delayed until Friday."</p>
          </div>
        </div>

        {showAdvanced && (
          <div className="mt-6 pt-6 border-t border-[#E4E4E7] space-y-4 animate-in fade-in slide-in-from-top-4 duration-300">
            <div>
              <h4 className="text-[11px] font-bold text-[#71717A] uppercase tracking-widest mb-2">Execution Pipeline</h4>
              <div className="flex flex-col gap-2">
                <div className="flex items-center gap-2 text-xs font-mono text-[#3F3F46]"><span className="text-green-600">✓</span> Intent verified via AXIOM Backend</div>
                <div className="flex items-center gap-2 text-xs font-mono text-[#3F3F46]"><span className="text-green-600">✓</span> Auth validated via Policy Engine</div>
                <div className="flex items-center gap-2 text-xs font-mono text-[#3F3F46]"><span className="text-[#3B82F6]">○</span> Pending API routing (slack/chat.postMessage)</div>
              </div>
            </div>
          </div>
        )}
      </div>
      <div className="px-6 py-4 border-t border-[#E4E4E7] bg-white flex justify-end gap-3">
        <button className="text-[#3F3F46] hover:text-[#18181B] px-6 py-2.5 rounded-xl text-[15px] font-semibold border border-[#E4E4E7] bg-white transition-colors">
          Cancel
        </button>
        <button className="bg-[#D97706] hover:bg-[#B45309] text-white px-8 py-2.5 rounded-xl text-[15px] font-semibold shadow-md transition-colors">
          Confirm & Send
        </button>
      </div>
    </div>
  );
}

function AuditTimeline() {
  const [showAdvanced, setShowAdvanced] = useState(false);

  return (
    <div className="mt-8 border border-[#E4E4E7] rounded-2xl bg-white overflow-hidden shadow-sm animate-in fade-in zoom-in-95 duration-500 delay-300 fill-mode-both min-w-[500px]">
      <div className="px-6 py-5 border-b border-[#E4E4E7] bg-[#FAFAFA] flex items-center justify-between">
        <h3 className="font-bold text-[#18181B] flex items-center gap-2">
           <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#71717A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
           Audit Log: Support Agent
        </h3>
        <button onClick={() => setShowAdvanced(!showAdvanced)} className="text-xs font-bold text-[#71717A] hover:text-[#18181B] flex items-center gap-1 transition-colors">
          {showAdvanced ? "Hide Detailed" : "View Detailed"} <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={`transition-transform duration-300 ${showAdvanced ? 'rotate-180' : ''}`}><polyline points="6 9 12 15 18 9"></polyline></svg>
        </button>
      </div>
      <div className="p-6 pt-8">
        <div className="relative border-l-2 border-[#E4E4E7] ml-2 space-y-10">
          <div className="relative">
            <div className="absolute -left-[29px] top-0 h-4 w-4 rounded-full bg-[#F4F4F5] border-[4px] border-white shadow-[0_0_0_1px_#E4E4E7]"></div>
            <div className="pl-6 -mt-1">
              <span className="text-[11px] font-bold text-[#A1A1AA] uppercase tracking-widest block mb-1">09:42</span>
              <p className="text-[15px] font-bold text-[#18181B]">Read Freshservice ticket FS-1832</p>
              <p className="text-[13px] font-medium text-[#71717A] mt-1.5 flex items-center gap-1.5"><span className="text-[#10B981] font-bold">✓</span> Authorized via policy</p>
              
              {showAdvanced && (
                 <div className="mt-3 p-3 bg-[#FAFAFA] border border-[#E4E4E7] rounded-lg text-[11px] font-mono text-[#71717A] space-y-1">
                   <p>Session ID: ax_sess_9a8b7c6d</p>
                   <p>Risk Score: 0.02 (LOW)</p>
                   <p>API Endpoint: GET /api/v2/tickets/FS-1832</p>
                 </div>
              )}
            </div>
          </div>
          
          <div className="relative">
            <div className="absolute -left-[29px] top-0 h-4 w-4 rounded-full bg-[#F4F4F5] border-[4px] border-white shadow-[0_0_0_1px_#E4E4E7]"></div>
            <div className="pl-6 -mt-1">
              <span className="text-[11px] font-bold text-[#A1A1AA] uppercase tracking-widest block mb-1">09:44</span>
              <p className="text-[15px] font-bold text-[#18181B]">Retrieved customer context</p>
              <p className="text-[13px] font-medium text-[#71717A] mt-1.5 flex items-center gap-1.5"><span className="text-[#10B981] font-bold">✓</span> Search across Slack and Jira</p>
            </div>
          </div>
          
          <div className="relative pb-2">
            <div className="absolute -left-[29px] top-0 h-4 w-4 rounded-full bg-[#EF4444] border-[4px] border-white shadow-[0_0_0_1px_#FECACA]"></div>
            <div className="pl-6 -mt-1">
              <span className="text-[11px] font-bold text-[#A1A1AA] uppercase tracking-widest block mb-1">09:46</span>
              <p className="text-[15px] font-bold text-[#18181B]">Attempted to access HR record</p>
              <div className="mt-3 bg-[#FEF2F2] border border-[#FECACA] rounded-xl px-4 py-3 shadow-sm">
                <span className="text-[11px] font-extrabold text-[#DC2626] uppercase tracking-widest flex items-center gap-1">DENIED</span>
                <p className="text-[13px] font-semibold text-[#991B1B] mt-1">HR records are restricted.</p>
              </div>
              
              {showAdvanced && (
                 <div className="mt-3 p-3 bg-[#FEF2F2]/50 border border-[#FECACA] rounded-lg text-[11px] font-mono text-[#DC2626] space-y-1">
                   <p>Error Code: ERR_ACCESS_DENIED_RBAC</p>
                   <p>Failed Policy: "Strict HR Separation"</p>
                   <p>Action Logged: Security incident generated (INC-921)</p>
                 </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function PermissionCheck() {
  return (
    <div className="mt-8 border border-[#FECACA] rounded-2xl bg-white overflow-hidden shadow-sm animate-in fade-in zoom-in-95 duration-500 delay-300 fill-mode-both min-w-[500px]">
      <div className="px-6 py-5 border-b border-[#FECACA] bg-[#FEF2F2] flex items-center justify-between">
        <h3 className="font-bold text-[#991B1B] flex items-center gap-2">
          <span className="w-8 h-8 rounded-full bg-white border border-[#FECACA] flex items-center justify-center text-sm">🛡️</span>
          Permission Check
        </h3>
        <span className="text-[10px] font-bold text-[#EF4444] uppercase tracking-widest bg-white px-2 py-1 rounded border border-[#FECACA]">Blocked</span>
      </div>
      <div className="p-6">
        <div className="space-y-4">
          <div className="flex justify-between items-center pb-4 border-b border-[#E4E4E7]">
            <span className="text-xs font-bold text-[#71717A] uppercase tracking-widest">Identity</span>
            <span className="text-sm font-semibold text-[#18181B]">admin@axiom.local (Engineering Manager)</span>
          </div>
          <div className="flex justify-between items-center pb-4 border-b border-[#E4E4E7]">
            <span className="text-xs font-bold text-[#71717A] uppercase tracking-widest">Requested Resource</span>
            <span className="text-sm font-mono text-[#3F3F46]">employee_compensation_records</span>
          </div>
          <div className="flex justify-between items-center pb-4 border-b border-[#E4E4E7]">
            <span className="text-xs font-bold text-[#71717A] uppercase tracking-widest">Active Policy</span>
            <span className="text-sm font-semibold text-[#3B82F6] hover:underline cursor-pointer">HR Compensation Policy</span>
          </div>
          <div className="flex justify-between items-center pt-2">
            <span className="text-xs font-bold text-[#71717A] uppercase tracking-widest">Result</span>
            <div className="flex items-center gap-2 text-sm font-bold text-[#EF4444]">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
              ACCESS DENIED
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
