"use client";

import { motion } from "framer-motion";
import { AgentState } from "@/lib/types";
import { 
  Database, Cloud, Newspaper, Calculator, 
  BrainCircuit, UserCheck, CheckCircle2,
  Workflow, AlertCircle
} from "lucide-react";
import { cn } from "@/lib/utils";

const NODE_ICONS = {
  start: Workflow,
  router: BrainCircuit,
  tool_executor: Database,
  human_gate: UserCheck,
  end: CheckCircle2,
};

const TOOL_ICONS = {
  query_database: Database,
  get_weather: Cloud,
  search_news: Newspaper,
  calculate: Calculator,
};

interface Props {
  state: AgentState;
}

export function DecisionTree({ state }: Props) {
  const { nodeHistory, currentNode, toolCalls, error } = state;

  return (
    <div className="flex flex-col gap-4 p-6 bg-zinc-900 rounded-xl border border-zinc-800 h-full overflow-y-auto w-full">
      <h3 className="text-zinc-100 font-semibold mb-2 flex items-center gap-2">
        <Workflow className="w-5 h-5 text-indigo-400" />
        Agent Decision Graph
      </h3>

      <div className="relative pl-6 space-y-8">
        {/* Vertical line connecting nodes */}
        <div className="absolute left-[31px] top-4 bottom-4 w-px bg-zinc-800" />

        {nodeHistory.map((event, idx) => {
          const NodeIcon = NODE_ICONS[event.node as keyof typeof NODE_ICONS] || Workflow;
          const isCurrent = currentNode === event.node && idx === nodeHistory.length - 1;
          
          return (
            <motion.div 
              key={`${event.node}-${idx}`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="relative z-10"
            >
              <div className="flex items-start gap-4">
                <div className={cn(
                  "w-10 h-10 rounded-full flex items-center justify-center border-2 bg-zinc-950 shrink-0",
                  isCurrent ? "border-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.5)]" : "border-zinc-700",
                  event.node === "human_gate" && "border-amber-500",
                  event.node === "end" && "border-emerald-500"
                )}>
                  <NodeIcon className={cn(
                    "w-5 h-5",
                    isCurrent ? "text-indigo-400" : "text-zinc-500",
                    event.node === "human_gate" && "text-amber-400",
                    event.node === "end" && "text-emerald-400"
                  )} />
                </div>
                
                <div className="pt-2">
                  <div className="text-sm font-medium text-zinc-200 capitalize">
                    {event.node.replace("_", " ")}
                  </div>
                  
                  {/* Show tool calls if this is the tool executor node */}
                  {event.node === "tool_executor" && (
                    <div className="mt-3 flex flex-col gap-2">
                      {toolCalls.map((tc) => {
                        const ToolIcon = TOOL_ICONS[tc.tool as keyof typeof TOOL_ICONS] || Workflow;
                        return (
                          <motion.div 
                            key={tc.id}
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            className="flex items-center gap-3 bg-zinc-950 border border-zinc-800 rounded-md py-2 px-3 text-xs"
                          >
                            <ToolIcon className="w-4 h-4 text-blue-400" />
                            <span className="text-zinc-300 font-mono">{tc.tool}()</span>
                            {tc.status === "pending" ? (
                              <span className="ml-auto flex w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                            ) : tc.status === "error" ? (
                              <span className="ml-auto text-red-400">Failed</span>
                            ) : (
                              <span className="ml-auto text-emerald-400 font-semibold">✓</span>
                            )}
                          </motion.div>
                        )
                      })}
                    </div>
                  )}
                  
                  {event.node === "human_gate" && state.requiresApproval && (
                    <div className="mt-2 text-xs text-amber-400 bg-amber-400/10 px-2 py-1 rounded inline-block">
                      Awaiting Human Approval
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          );
        })}

        {/* Current pulsing node if processing */}
        {state.isProcessing && currentNode && currentNode !== nodeHistory[nodeHistory.length - 1]?.node && (
           <motion.div 
             initial={{ opacity: 0 }} animate={{ opacity: 1 }}
             className="relative z-10 flex items-start gap-4"
           >
             <div className="w-10 h-10 rounded-full flex items-center justify-center border-2 border-indigo-500/50 bg-zinc-950 animate-pulse shrink-0">
               <div className="w-2 h-2 bg-indigo-400 rounded-full" />
             </div>
             <div className="pt-2">
               <div className="text-sm font-medium text-emerald-400 animate-pulse">Running graph...</div>
             </div>
           </motion.div>
        )}

        {/* Error State */}
        {error && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="relative z-10">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-full flex items-center justify-center border-2 border-red-500 bg-red-950 shrink-0">
                <AlertCircle className="w-5 h-5 text-red-500" />
              </div>
              <div className="pt-2">
                <div className="text-sm font-medium text-red-400">Execution Failed</div>
                <div className="text-xs text-red-400/80 mt-1 max-w-xs break-words">{error}</div>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
