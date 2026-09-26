"use client";
import React, { useEffect, useState, useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";

export default function KnowledgeGraph() {
  const [graphData, setGraphData] = useState<{ nodes: any[]; links: any[] }>({ nodes: [], links: [] });
  const [isLoading, setIsLoading] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [selectedNode, setSelectedNode] = useState<any>(null);

  useEffect(() => {
    if (containerRef.current) {
      setDimensions({
        width: containerRef.current.clientWidth,
        height: containerRef.current.clientHeight || 600
      });
    }

    fetch("http://localhost:8000/api/memory/graph")
      .then((res) => res.json())
      .then((data) => {
        setGraphData(data);
        setIsLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setIsLoading(false);
      });
  }, []);

  if (isLoading) {
    return <div className="flex justify-center items-center h-full min-h-[400px] text-[#64748B]">Retrieving Organizational Context Graph...</div>;
  }

  return (
    <div ref={containerRef} className="w-full h-full min-h-[500px] bg-[#FAFAFA] rounded-xl overflow-hidden relative border border-[#E4E4E7]">
      <div className="absolute top-4 left-4 z-10 bg-white shadow-md border border-[#E4E4E7] px-5 py-4 rounded-xl text-xs text-[#71717A] backdrop-blur-md bg-white/90">
        <h3 className="font-bold text-[#18181B] mb-1">Enterprise Knowledge Graph</h3>
        <p className="font-medium">{graphData.nodes.length} Nodes • {graphData.links.length} Relationships</p>
        <div className="flex flex-wrap gap-3 mt-3">
          <span className="flex items-center gap-1.5 font-semibold text-[#18181B]"><span className="w-2 h-2 rounded-full bg-[#18181B] shadow-[0_0_8px_#18181B]"></span> People</span>
          <span className="flex items-center gap-1.5 font-semibold text-[#18181B]"><span className="w-2 h-2 rounded-full bg-[#2563EB] shadow-[0_0_8px_#3B82F6]"></span> Jira</span>
          <span className="flex items-center gap-1.5 font-semibold text-[#18181B]"><span className="w-2 h-2 rounded-full bg-[#64748B] shadow-[0_0_8px_#94A3B8]"></span> Slack</span>
          <span className="flex items-center gap-1.5 font-semibold text-[#18181B]"><span className="w-2 h-2 rounded-full bg-[#10B981] shadow-[0_0_8px_#34D399]"></span> Freshservice</span>
          <span className="flex items-center gap-1.5 font-semibold text-[#18181B]"><span className="w-2 h-2 rounded-full bg-[#EAB308] shadow-[0_0_8px_#FCD34D]"></span> Github</span>
          <span className="flex items-center gap-1.5 font-semibold text-[#18181B]"><span className="w-2 h-2 rounded-full bg-[#EF4444] shadow-[0_0_8px_#F87171]"></span> Notion</span>
          <span className="flex items-center gap-1.5 font-semibold text-[#18181B]"><span className="w-2 h-2 rounded-full bg-[#8B5CF6] shadow-[0_0_8px_#A78BFA]"></span> Other</span>
        </div>
      </div>
      
      {selectedNode && (
        <div className="absolute top-4 right-4 z-10 bg-white shadow-xl border border-[#E4E4E7] w-80 rounded-xl overflow-hidden animate-in slide-in-from-right-4 fade-in duration-300">
          <div className="px-5 py-4 border-b border-[#E4E4E7] flex justify-between items-center bg-gradient-to-r from-[#FAFAFA] to-white">
            <h3 className="font-bold text-[#18181B] truncate max-w-[200px]">{selectedNode.label}</h3>
            <button onClick={() => setSelectedNode(null)} className="text-[#A1A1AA] hover:text-[#18181B]">✕</button>
          </div>
          <div className="p-5 space-y-4">
            <div>
              <p className="text-[10px] font-bold text-[#71717A] uppercase tracking-widest mb-1">Source System</p>
              <p className="text-sm font-semibold capitalize text-[#18181B] flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${
                  selectedNode.group === 'person' ? 'bg-[#18181B]' :
                  selectedNode.group === 'jira' ? 'bg-[#2563EB]' : 
                  selectedNode.group === 'slack' ? 'bg-[#64748B]' : 
                  selectedNode.group === 'freshservice' ? 'bg-[#10B981]' : 
                  selectedNode.group === 'github' ? 'bg-[#EAB308]' :
                  selectedNode.group === 'notion' ? 'bg-[#EF4444]' :
                  'bg-[#8B5CF6]'
                }`}></span>
                {selectedNode.group}
              </p>
            </div>
            <div>
              <p className="text-[10px] font-bold text-[#71717A] uppercase tracking-widest mb-1">Entity ID</p>
              <p className="text-xs font-mono text-[#3F3F46] bg-[#FAFAFA] p-2 rounded border border-[#E4E4E7]">{selectedNode.id}</p>
            </div>
            <div>
              <p className="text-[10px] font-bold text-[#71717A] uppercase tracking-widest mb-1">Contextual Payload</p>
              <p className="text-sm text-[#3F3F46] leading-relaxed">Extracted context vector indicating high relevance to Project Atlas and active support escalations.</p>
            </div>
            <button className="w-full mt-2 bg-[#18181B] hover:bg-[#3B82F6] text-white py-2.5 rounded-lg text-sm font-semibold transition-colors shadow-sm">
              Explore Connections
            </button>
          </div>
        </div>
      )}
      
      <ForceGraph2D
        width={dimensions.width}
        height={dimensions.height}
        graphData={graphData}
        nodeColor={(node: any) => {
          if (node === selectedNode) return "#38BDF8"; // Highlight selected in a bright blue
          if (node.group === "person") return "#18181B";
          if (node.group === "jira") return "#2563EB";
          if (node.group === "slack") return "#64748B";
          if (node.group === "freshservice") return "#10B981";
          if (node.group === "github") return "#EAB308";
          if (node.group === "notion") return "#EF4444";
          return "#8B5CF6";
        }}
        nodeRelSize={7}
        onNodeClick={(node) => setSelectedNode(node)}
        linkColor={() => "rgba(0,0,0,0.15)"}
        backgroundColor="transparent"
        linkDirectionalParticles={3}
        linkDirectionalParticleSpeed={0.005}
        linkDirectionalParticleWidth={2}
      />
    </div>
  );
}
