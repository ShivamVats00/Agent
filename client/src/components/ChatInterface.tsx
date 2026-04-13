"use client";

import { useState } from "react";
import { Send, Settings, Sparkles, Bot, AlertTriangle, UserCheck } from "lucide-react";
import { AgentState } from "@/lib/types";
import { motion } from "framer-motion";

interface Props {
  state: AgentState;
  onSend: (message: string, requireApproval: boolean) => void;
  onDisconnect: () => void;
}

export function ChatInterface({ state, onSend, onDisconnect }: Props) {
  const [input, setInput] = useState("");
  const [requireApproval, setRequireApproval] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || state.isProcessing) return;
    
    // Generate a fresh thread ID for each task to keep it simple
    const threadId = `thread-${Date.now()}`;
    onSend(input, requireApproval);
    setInput("");
  };

  return (
    <div className="flex flex-col h-full bg-zinc-900 rounded-xl border border-zinc-800 overflow-hidden">
      {/* Header */}
      <div className="bg-zinc-950 p-4 border-b border-zinc-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30">
            <Sparkles className="w-4 h-4 text-indigo-400" />
          </div>
          <div>
            <h2 className="font-semibold text-zinc-100">Agentic Workspace</h2>
            <div className="flex items-center gap-2 text-xs text-zinc-500">
              <span className="flex items-center gap-1">
                <span className={`w-2 h-2 rounded-full ${state.isProcessing ? 'bg-indigo-500 animate-pulse' : 'bg-zinc-600'}`} />
                {state.isProcessing ? 'Processing' : 'Idle'}
              </span>
              <span>·</span>
              <span>Gemini 2.0 Flash</span>
            </div>
          </div>
        </div>
        
        {state.isProcessing && (
          <button 
            onClick={onDisconnect}
            className="text-xs text-red-400 hover:text-red-300 px-3 py-1.5 bg-red-400/10 rounded-md transition-colors"
          >
            Cancel Run
          </button>
        )}
      </div>

      {/* Message History */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {state.messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-zinc-500 p-8 text-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-zinc-800/50 flex items-center justify-center mb-2 shadow-inner">
              <Bot className="w-8 h-8 text-zinc-600" />
            </div>
            <p className="max-w-md break-words">
              I'm an autonomous agent with access to a database, weather API, news search, and math calculator.
            </p>
            <div className="flex flex-wrap justify-center gap-2 mt-2">
              <span className="px-3 py-1 bg-zinc-800 rounded-full text-xs cursor-pointer hover:bg-zinc-700 transition" onClick={() => setInput("Compare the weather in Tokyo and Paris.")}>
                Weather search
              </span>
              <span className="px-3 py-1 bg-zinc-800 rounded-full text-xs cursor-pointer hover:bg-zinc-700 transition" onClick={() => setInput("Search news for AI agents and summarize.")}>
                News summary
              </span>
            </div>
          </div>
        ) : (
          state.messages.map((msg, idx) => (
            <motion.div 
              key={msg.id || idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-3 max-w-[90%] ${msg.role === "user" ? "ml-auto flex-row-reverse" : ""}`}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                msg.role === "user" 
                  ? "bg-zinc-800 text-zinc-400" 
                  : "bg-indigo-500/20 text-indigo-400 border border-indigo-500/30"
              }`}>
                {msg.role === "user" ? <UserCheck className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>
              
              <div className={`p-4 rounded-2xl text-sm leading-relaxed ${
                msg.role === "user" 
                  ? "bg-zinc-800 text-zinc-200 rounded-tr-sm" 
                  : "bg-zinc-950 border border-zinc-800 text-zinc-300 rounded-tl-sm shadow-inner"
              }`}>
                <div className="whitespace-pre-wrap">{msg.content}</div>
                
                {msg.role === "agent" && idx === state.messages.length - 1 && state.isProcessing && (
                  <span className="inline-block w-1.5 h-4 ml-1 bg-indigo-500 animate-pulse align-middle" />
                )}
              </div>
            </motion.div>
          ))
        )}
      </div>

      {/* Input Form */}
      <div className="p-4 bg-zinc-950 border-t border-zinc-800">
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <div className="relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Give the agent a complex multi-step task..."
              className="w-full bg-zinc-900 border border-zinc-800 rounded-xl pl-4 pr-12 py-3 text-sm text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 resize-none h-14"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />
            <button
              type="submit"
              disabled={!input.trim() || state.isProcessing}
              className="absolute right-2 top-2 p-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          
          <div className="flex items-center justify-between px-1">
            <label className="flex items-center gap-2 text-xs text-zinc-500 cursor-pointer group">
              <input 
                type="checkbox" 
                checked={requireApproval}
                onChange={(e) => setRequireApproval(e.target.checked)}
                className="rounded border-zinc-700 bg-zinc-900 text-indigo-500 focus:ring-indigo-500/50"
              />
              <span className="group-hover:text-zinc-400 transition-colors flex items-center gap-1.5">
                <AlertTriangle className="w-3 h-3 text-amber-500" />
                Require human approval before final response
              </span>
            </label>
            
            <div className="text-xs text-zinc-600 flex items-center gap-1">
              <Settings className="w-3 h-3" /> Tools enabled: 4
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
