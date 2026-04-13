"use client";

import { AgentState } from "@/lib/types";
import { Terminal, Check, AlertCircle, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export function ToolCallLog({ state }: { state: AgentState }) {
  if (state.toolCalls.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-zinc-500 text-sm flex-col gap-2">
        <Terminal className="w-8 h-8 opacity-50" />
        <p>No tools executed yet</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2 h-full overflow-y-auto font-mono text-xs p-4 bg-black rounded-xl border border-zinc-800">
      <div className="sticky top-0 bg-black/90 backdrop-blur pb-2 border-b border-zinc-800 mb-2 flex items-center justify-between z-10">
        <span className="text-zinc-400">Execution Log</span>
        <span className="text-zinc-500">{state.toolCalls.length} invocations</span>
      </div>

      <AnimatePresence>
        {state.toolCalls.map((tc, idx) => (
          <motion.div 
            key={tc.id || idx}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col gap-1.5 border-l-2 pl-3 py-1 mb-2 border-zinc-800"
          >
            <div className="flex items-center gap-2">
              {tc.status === "pending" && <Loader2 className="w-3 h-3 text-blue-400 animate-spin" />}
              {tc.status === "success" && <Check className="w-3 h-3 text-emerald-400" />}
              {tc.status === "error" && <AlertCircle className="w-3 h-3 text-red-400" />}
              
              <span className="text-blue-400 font-semibold">{tc.tool}</span>
              <span className="text-zinc-500">v{state.stepCount}</span>
            </div>
            
            <div className="text-zinc-400 pl-5">
              <span className="text-zinc-500">Args:</span> {JSON.stringify(tc.args)}
            </div>
            
            {tc.result && (
              <div className="mt-1 pl-5">
                <span className="text-zinc-500 block mb-1">Result:</span>
                <div className="bg-zinc-900/50 p-2 rounded border border-zinc-800/50 text-zinc-300 max-h-32 overflow-y-auto break-all">
                  {tc.result.length > 300 ? tc.result.substring(0, 300) + "..." : tc.result}
                </div>
              </div>
            )}
          </motion.div>
        ))}
      </AnimatePresence>
      
      {/* Auto-scroll anchor */}
      <div className="mt-auto h-1" />
    </div>
  );
}
