"use client";
import React, { useState } from "react";

export default function Settings({ onClose }: { onClose: () => void }) {
  const [activeTab, setActiveTab] = useState<"account" | "integrations" | "access">("account");
  const [toast, setToast] = useState<string | null>(null);

  // States for sub-pages
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [jiraConnected, setJiraConnected] = useState(false);
  const [isConnectingJira, setIsConnectingJira] = useState(false);
  
  const [anthropicKey, setAnthropicKey] = useState("sk-ant-api03-xxxx-xxxx");
  const [isUpdatingKey, setIsUpdatingKey] = useState(false);

  const [agentKeys, setAgentKeys] = useState([
    { id: 1, name: "Support Agent", hint: "ax_live_...94b2", date: "Oct 12, 2024" }
  ]);

  const [nlpPolicyInput, setNlpPolicyInput] = useState("");
  const [isGeneratingPolicy, setIsGeneratingPolicy] = useState(false);
  const [generatedPolicies, setGeneratedPolicies] = useState<any[]>([]);

  const showToast = (message: string) => {
    setToast(message);
    setTimeout(() => setToast(null), 3000);
  };

  const handleLogout = () => {
    setIsLoggingOut(true);
    setTimeout(() => {
      setIsLoggingOut(false);
      showToast("Logged out successfully.");
      onClose(); // In a real app this would route to /login
    }, 1000);
  };

  const handleConnectJira = () => {
    setIsConnectingJira(true);
    setTimeout(() => {
      setIsConnectingJira(false);
      setJiraConnected(true);
      showToast("Jira connected successfully to acme.atlassian.net");
    }, 1500);
  };

  const handleUpdateKey = () => {
    setIsUpdatingKey(true);
    setTimeout(() => {
      setIsUpdatingKey(false);
      showToast("Anthropic API key verified and updated.");
    }, 1000);
  };

  const handleGenerateKey = () => {
    const newKey = {
      id: Date.now(),
      name: "New DevOps Agent",
      hint: `ax_live_...${Math.floor(Math.random()*10000)}`,
      date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    };
    setAgentKeys([...agentKeys, newKey]);
    showToast("Generated new API key.");
  };

  const handleRevokeKey = (id: number) => {
    setAgentKeys(agentKeys.filter(k => k.id !== id));
    showToast("Agent key revoked globally.");
  };

  const handleGeneratePolicy = () => {
    if (!nlpPolicyInput.trim()) return;
    setIsGeneratingPolicy(true);
    setTimeout(() => {
      setIsGeneratingPolicy(false);
      setGeneratedPolicies([...generatedPolicies, {
        id: Date.now(),
        intent: nlpPolicyInput,
        json: `{
  "Effect": "Allow",
  "Action": ["jira:ViewTicket"],
  "Condition": { "Role": "Engineer" }
}`
      }]);
      setNlpPolicyInput("");
      showToast("NLP Policy translated to JSON RBAC successfully.");
    }, 1500);
  };

  const handleDeletePolicy = (id: number) => {
    setGeneratedPolicies(generatedPolicies.filter(p => p.id !== id));
    showToast("Policy permanently deleted.");
  };

  return (
    <div className="flex flex-col h-full w-full bg-[#FAFAFA] relative">
      {toast && (
        <div className="absolute top-4 right-4 z-50 bg-[#18181B] text-white px-4 py-3 rounded-lg shadow-xl text-sm font-medium animate-in slide-in-from-top-2 fade-in flex items-center gap-2">
          <span className="text-[#10B981]">✓</span> {toast}
        </div>
      )}

      <header className="flex-shrink-0 flex items-center justify-between px-8 py-5 bg-white/80 backdrop-blur-xl sticky top-0 z-10 border-b border-[#E4E4E7]">
         <div className="flex items-center gap-4">
           <h2 className="text-xl font-black tracking-tighter text-[#18181B]">AXIOM Settings</h2>
         </div>
         <button onClick={onClose} className="text-sm font-bold text-[#71717A] hover:text-[#18181B] px-4 py-2 bg-[#F4F4F5] border border-transparent hover:border-[#E4E4E7] rounded-full transition-all shadow-sm">
            Close Panel
         </button>
      </header>

      <div className="flex-1 overflow-y-auto px-8 py-8">
        <div className="w-full max-w-5xl mx-auto flex gap-8">
          
          {/* Settings Sidebar */}
          <div className="w-64 flex-shrink-0 space-y-2">
            <button 
              onClick={() => setActiveTab("account")}
              className={`w-full text-left px-4 py-3 rounded-xl text-sm font-bold transition-all ${activeTab === 'account' ? 'bg-white shadow-sm border border-[#E4E4E7] text-[#18181B]' : 'text-[#71717A] hover:bg-white/50 hover:text-[#18181B] border border-transparent'}`}
            >
              Account & Security
            </button>
            <button 
              onClick={() => setActiveTab("integrations")}
              className={`w-full text-left px-4 py-3 rounded-xl text-sm font-bold transition-all ${activeTab === 'integrations' ? 'bg-white shadow-sm border border-[#E4E4E7] text-[#18181B]' : 'text-[#71717A] hover:bg-white/50 hover:text-[#18181B] border border-transparent'}`}
            >
              Integrations Mesh
            </button>
            <button 
              onClick={() => setActiveTab("access")}
              className={`w-full text-left px-4 py-3 rounded-xl text-sm font-bold transition-all ${activeTab === 'access' ? 'bg-white shadow-sm border border-[#E4E4E7] text-[#18181B]' : 'text-[#71717A] hover:bg-white/50 hover:text-[#18181B] border border-transparent'}`}
            >
              Access & Policies
            </button>
          </div>

          {/* Settings Content */}
          <div className="flex-1 bg-white border border-[#E4E4E7] shadow-sm rounded-2xl p-8 min-h-[600px]">
            
            {activeTab === "account" && (
              <div className="space-y-8 animate-in fade-in zoom-in-95 duration-300">
                <div>
                  <h3 className="text-xl font-bold text-[#18181B] mb-2">Account & Security</h3>
                  <p className="text-sm text-[#71717A]">Manage your root user identity and session bounds.</p>
                </div>
                <div className="border-t border-[#E4E4E7] pt-6 space-y-6">
                  <div className="flex justify-between items-center bg-[#FAFAFA] p-5 rounded-xl border border-[#E4E4E7]">
                    <div>
                      <p className="text-[11px] font-bold text-[#71717A] uppercase tracking-widest mb-1">Authenticated Principal</p>
                      <p className="text-base font-bold text-[#18181B]">admin@axiom.local</p>
                      <span className="inline-block mt-2 px-2 py-1 bg-[#EFF6FF] text-[#2563EB] text-[10px] font-bold rounded-md uppercase tracking-wider">Engineering Manager</span>
                    </div>
                  </div>
                  <div>
                    <button 
                      onClick={handleLogout}
                      disabled={isLoggingOut}
                      className="px-6 py-2.5 bg-[#FEF2F2] border border-[#FECACA] text-[#DC2626] rounded-xl text-sm font-bold hover:bg-[#FEE2E2] transition-colors disabled:opacity-50"
                    >
                      {isLoggingOut ? "Disconnecting Session..." : "Terminate Session"}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "integrations" && (
              <div className="space-y-8 animate-in fade-in zoom-in-95 duration-300">
                <div>
                  <h3 className="text-xl font-bold text-[#18181B] mb-2">Integrations</h3>
                  <p className="text-sm text-[#71717A]">Connect AXIOM to your enterprise systems via MCP.</p>
                </div>
                <div className="border-t border-[#E4E4E7] pt-6 space-y-4">
                  
                  {/* Slack */}
                  <div className="flex items-center justify-between p-5 border border-[#E4E4E7] rounded-xl bg-[#FAFAFA]">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-[#4A154B] rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-sm">S</div>
                      <div>
                        <p className="text-base font-bold text-[#18181B]">Slack</p>
                        <p className="text-xs font-medium text-[#10B981] flex items-center gap-1.5"><span className="w-1.5 h-1.5 bg-[#10B981] rounded-full"></span> Synced: acme-corp.slack.com</p>
                      </div>
                    </div>
                    <button onClick={() => showToast("Slack settings synced.")} className="px-5 py-2 bg-white border border-[#E4E4E7] text-[#3F3F46] rounded-xl text-sm font-bold hover:bg-[#F4F4F5] shadow-sm">Re-Sync</button>
                  </div>
                  
                  {/* Jira */}
                  <div className="flex items-center justify-between p-5 border border-[#E4E4E7] rounded-xl bg-[#FAFAFA]">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-[#0052CC] rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-sm">J</div>
                      <div>
                        <p className="text-base font-bold text-[#18181B]">Jira</p>
                        {jiraConnected ? (
                           <p className="text-xs font-medium text-[#10B981] flex items-center gap-1.5"><span className="w-1.5 h-1.5 bg-[#10B981] rounded-full"></span> Synced: acme.atlassian.net</p>
                        ) : (
                           <p className="text-xs font-medium text-[#71717A] flex items-center gap-1.5"><span className="w-1.5 h-1.5 bg-[#A1A1AA] rounded-full"></span> Disconnected</p>
                        )}
                      </div>
                    </div>
                    {jiraConnected ? (
                      <button onClick={() => showToast("Jira settings synced.")} className="px-5 py-2 bg-white border border-[#E4E4E7] text-[#3F3F46] rounded-xl text-sm font-bold hover:bg-[#F4F4F5] shadow-sm">Re-Sync</button>
                    ) : (
                      <button 
                        onClick={handleConnectJira}
                        disabled={isConnectingJira}
                        className="px-5 py-2 bg-[#18181B] text-white rounded-xl text-sm font-bold hover:bg-[#3B82F6] transition-colors shadow-md disabled:opacity-50"
                      >
                        {isConnectingJira ? "Connecting..." : "Initialize Oauth"}
                      </button>
                    )}
                  </div>

                  {/* Freshservice */}
                  <div className="flex items-center justify-between p-5 border border-[#E4E4E7] rounded-xl bg-[#FAFAFA]">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-[#10B981] rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-sm">F</div>
                      <div>
                        <p className="text-base font-bold text-[#18181B]">Freshservice</p>
                        <p className="text-xs font-medium text-[#10B981] flex items-center gap-1.5"><span className="w-1.5 h-1.5 bg-[#10B981] rounded-full"></span> Synced: acme.freshservice.com</p>
                      </div>
                    </div>
                    <button onClick={() => showToast("Freshservice settings synced.")} className="px-5 py-2 bg-white border border-[#E4E4E7] text-[#3F3F46] rounded-xl text-sm font-bold hover:bg-[#F4F4F5] shadow-sm">Re-Sync</button>
                  </div>

                  {/* GitHub */}
                  <div className="flex items-center justify-between p-5 border border-[#E4E4E7] rounded-xl bg-[#FAFAFA]">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-[#18181B] rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-sm">G</div>
                      <div>
                        <p className="text-base font-bold text-[#18181B]">GitHub</p>
                        <p className="text-xs font-medium text-[#10B981] flex items-center gap-1.5"><span className="w-1.5 h-1.5 bg-[#10B981] rounded-full"></span> Synced: acme-corp</p>
                      </div>
                    </div>
                    <button onClick={() => showToast("GitHub settings synced.")} className="px-5 py-2 bg-white border border-[#E4E4E7] text-[#3F3F46] rounded-xl text-sm font-bold hover:bg-[#F4F4F5] shadow-sm">Re-Sync</button>
                  </div>

                  {/* Notion */}
                  <div className="flex items-center justify-between p-5 border border-[#E4E4E7] rounded-xl bg-[#FAFAFA]">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-white border border-[#E4E4E7] rounded-xl flex items-center justify-center text-[#18181B] font-bold text-xl shadow-sm">N</div>
                      <div>
                        <p className="text-base font-bold text-[#18181B]">Notion</p>
                        <p className="text-xs font-medium text-[#10B981] flex items-center gap-1.5"><span className="w-1.5 h-1.5 bg-[#10B981] rounded-full"></span> Synced: acme-wiki</p>
                      </div>
                    </div>
                    <button onClick={() => showToast("Notion settings synced.")} className="px-5 py-2 bg-white border border-[#E4E4E7] text-[#3F3F46] rounded-xl text-sm font-bold hover:bg-[#F4F4F5] shadow-sm">Re-Sync</button>
                  </div>

                  {/* Google Drive */}
                  <div className="flex items-center justify-between p-5 border border-[#E4E4E7] rounded-xl bg-[#FAFAFA]">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-[#3B82F6] rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-sm">D</div>
                      <div>
                        <p className="text-base font-bold text-[#18181B]">Google Drive</p>
                        <p className="text-xs font-medium text-[#10B981] flex items-center gap-1.5"><span className="w-1.5 h-1.5 bg-[#10B981] rounded-full"></span> Synced: acme.local</p>
                      </div>
                    </div>
                    <button onClick={() => showToast("Google Drive settings synced.")} className="px-5 py-2 bg-white border border-[#E4E4E7] text-[#3F3F46] rounded-xl text-sm font-bold hover:bg-[#F4F4F5] shadow-sm">Re-Sync</button>
                  </div>

                  {/* Linear */}
                  <div className="flex items-center justify-between p-5 border border-[#E4E4E7] rounded-xl bg-[#FAFAFA]">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-[#5E6AD2] rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-sm">L</div>
                      <div>
                        <p className="text-base font-bold text-[#18181B]">Linear</p>
                        <p className="text-xs font-medium text-[#71717A] flex items-center gap-1.5"><span className="w-1.5 h-1.5 bg-[#A1A1AA] rounded-full"></span> Disconnected</p>
                      </div>
                    </div>
                    <button onClick={() => showToast("OAuth initialized.")} className="px-5 py-2 bg-[#18181B] text-white rounded-xl text-sm font-bold hover:bg-[#3B82F6] transition-colors shadow-md">Initialize OAuth</button>
                  </div>

                  {/* PagerDuty */}
                  <div className="flex items-center justify-between p-5 border border-[#E4E4E7] rounded-xl bg-[#FAFAFA]">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-[#06AC38] rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-sm">P</div>
                      <div>
                        <p className="text-base font-bold text-[#18181B]">PagerDuty</p>
                        <p className="text-xs font-medium text-[#10B981] flex items-center gap-1.5"><span className="w-1.5 h-1.5 bg-[#10B981] rounded-full"></span> Synced: acme-oncall</p>
                      </div>
                    </div>
                    <button onClick={() => showToast("PagerDuty settings synced.")} className="px-5 py-2 bg-white border border-[#E4E4E7] text-[#3F3F46] rounded-xl text-sm font-bold hover:bg-[#F4F4F5] shadow-sm">Re-Sync</button>
                  </div>

                  {/* Datadog */}
                  <div className="flex items-center justify-between p-5 border border-[#E4E4E7] rounded-xl bg-[#FAFAFA]">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-[#632CA6] rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-sm">DD</div>
                      <div>
                        <p className="text-base font-bold text-[#18181B]">Datadog</p>
                        <p className="text-xs font-medium text-[#10B981] flex items-center gap-1.5"><span className="w-1.5 h-1.5 bg-[#10B981] rounded-full"></span> Synced: acme-monitoring</p>
                      </div>
                    </div>
                    <button onClick={() => showToast("Datadog settings synced.")} className="px-5 py-2 bg-white border border-[#E4E4E7] text-[#3F3F46] rounded-xl text-sm font-bold hover:bg-[#F4F4F5] shadow-sm">Re-Sync</button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "access" && (
              <div className="space-y-8 animate-in fade-in zoom-in-95 duration-300">
                <div>
                  <h3 className="text-xl font-bold text-[#18181B] mb-2">Access & Policies</h3>
                  <p className="text-sm text-[#71717A]">Manage sub-agent tokens and natural language RBAC controls.</p>
                </div>
                
                {/* NLP RBAC Section */}
                <div className="border-t border-[#E4E4E7] pt-6">
                  <h4 className="text-[13px] font-bold text-[#18181B] uppercase tracking-wider mb-4">NLP-Based RBAC Generator</h4>
                  <div className="bg-[#FAFAFA] p-5 rounded-xl border border-[#E4E4E7]">
                    <label className="block text-[11px] font-bold text-[#71717A] uppercase tracking-widest mb-3">Define Policy via Natural Language</label>
                    <div className="flex gap-3">
                      <input 
                        type="text" 
                        placeholder="e.g. Allow engineers to view jira tickets but not edit them"
                        value={nlpPolicyInput} 
                        onChange={(e) => setNlpPolicyInput(e.target.value)}
                        className="flex-1 border border-[#E4E4E7] bg-white rounded-xl px-4 py-3 text-[14px] font-medium text-[#18181B] focus:outline-none focus:border-[#3B82F6] shadow-inner" 
                        onKeyDown={(e) => e.key === 'Enter' && handleGeneratePolicy()}
                      />
                      <button 
                        onClick={handleGeneratePolicy}
                        disabled={isGeneratingPolicy || !nlpPolicyInput.trim()}
                        className="px-6 py-3 bg-[#18181B] hover:bg-[#3B82F6] text-white rounded-xl text-sm font-bold transition-colors shadow-md disabled:opacity-50"
                      >
                        {isGeneratingPolicy ? "Compiling..." : "Generate Rule"}
                      </button>
                    </div>
                    
                    {generatedPolicies.length > 0 && (
                      <div className="mt-6 space-y-4">
                        <p className="text-[11px] font-bold text-[#71717A] uppercase tracking-widest">Compiled Policies</p>
                        {generatedPolicies.map(pol => (
                          <div key={pol.id} className="bg-white border border-[#E4E4E7] rounded-xl overflow-hidden shadow-sm">
                            <div className="px-4 py-3 bg-[#F8F9FA] border-b border-[#E4E4E7] flex justify-between items-center">
                              <p className="text-sm font-semibold text-[#18181B]">"{pol.intent}"</p>
                              <div className="flex gap-2 items-center">
                                <span className="px-2 py-1 bg-[#ECFDF5] text-[#059669] text-[10px] font-bold uppercase rounded border border-[#A7F3D0]">Active</span>
                                <button onClick={() => handleDeletePolicy(pol.id)} className="text-[#A1A1AA] hover:text-[#DC2626] transition-colors p-1" title="Delete Policy">
                                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 6h18"></path><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path></svg>
                                </button>
                              </div>
                            </div>
                            <pre className="p-4 text-xs font-mono text-[#3F3F46] overflow-x-auto">
                              {pol.json}
                            </pre>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <div className="border-t border-[#E4E4E7] pt-6 space-y-6">
                  <div className="bg-[#FAFAFA] p-5 rounded-xl border border-[#E4E4E7]">
                    <label className="block text-[11px] font-bold text-[#71717A] uppercase tracking-widest mb-3">Anthropic API Key (Claude Engine)</label>
                    <div className="flex gap-3">
                      <input 
                        type="password" 
                        value={anthropicKey} 
                        onChange={(e) => setAnthropicKey(e.target.value)}
                        className="flex-1 border border-[#E4E4E7] bg-white rounded-xl px-4 py-3 text-[15px] font-medium text-[#18181B] focus:outline-none focus:border-[#3B82F6] shadow-inner" 
                      />
                      <button 
                        onClick={handleUpdateKey}
                        disabled={isUpdatingKey}
                        className="px-6 py-3 bg-[#18181B] hover:bg-[#3B82F6] text-white rounded-xl text-sm font-bold transition-colors shadow-md disabled:opacity-50"
                      >
                        {isUpdatingKey ? "Verifying..." : "Update Engine"}
                      </button>
                    </div>
                    <p className="text-xs font-medium text-[#71717A] mt-3">Required for AXIOM reasoning and conversational memory graphs.</p>
                  </div>
                </div>
                
                <div className="border-t border-[#E4E4E7] pt-6">
                  <div className="flex justify-between items-center mb-4">
                    <h4 className="text-sm font-bold text-[#18181B] uppercase tracking-wider">Agent API Keys</h4>
                    <button onClick={handleGenerateKey} className="text-sm text-[#2563EB] font-bold hover:text-[#1D4ED8] bg-[#EFF6FF] px-4 py-2 rounded-lg transition-colors">
                      + Generate API Token
                    </button>
                  </div>
                  
                  <div className="border border-[#E4E4E7] rounded-xl overflow-hidden shadow-sm">
                    <table className="w-full text-left text-sm">
                      <thead className="bg-[#FAFAFA] text-[#71717A]">
                        <tr>
                          <th className="px-5 py-4 font-bold text-[11px] uppercase tracking-widest">Agent Identity</th>
                          <th className="px-5 py-4 font-bold text-[11px] uppercase tracking-widest">Key Prefix</th>
                          <th className="px-5 py-4 font-bold text-[11px] uppercase tracking-widest">Initialization</th>
                          <th className="px-5 py-4 font-bold text-[11px] uppercase tracking-widest text-right">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#E4E4E7]">
                        {agentKeys.length === 0 && (
                           <tr><td colSpan={4} className="px-5 py-8 text-center text-[#A1A1AA] font-medium">No active agent keys.</td></tr>
                        )}
                        {agentKeys.map(key => (
                          <tr key={key.id} className="hover:bg-[#FAFAFA] transition-colors">
                            <td className="px-5 py-4 font-bold text-[#18181B]">{key.name}</td>
                            <td className="px-5 py-4 text-[#71717A] font-mono text-xs bg-gray-50">{key.hint}</td>
                            <td className="px-5 py-4 text-[#71717A] font-medium">{key.date}</td>
                            <td className="px-5 py-4 text-right">
                              <button onClick={() => handleRevokeKey(key.id)} className="text-[#EF4444] hover:text-[#B91C1C] font-bold bg-[#FEF2F2] px-3 py-1.5 rounded-lg transition-colors">Revoke</button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

              </div>
            )}
            
          </div>
        </div>
      </div>
    </div>
  );
}
