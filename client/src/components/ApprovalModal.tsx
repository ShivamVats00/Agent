"use client";

import { motion } from "framer-motion";
import { ShieldAlert, Check, X } from "lucide-react";
import { submitApproval } from "@/lib/api";
import { useState } from "react";

interface Props {
  threadId: string;
  summary: string;
  onDecision: (decision: "approved" | "rejected") => void;
}

export function ApprovalModal({ threadId, summary, onDecision }: Props) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleDecision = async (decision: "approved" | "rejected") => {
    setIsSubmitting(true);
    try {
      await submitApproval(threadId, decision);
      onDecision(decision);
    } catch (e) {
      console.error("Failed to submit approval", e);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        className="bg-zinc-900 border border-amber-500/30 shadow-[0_0_40px_rgba(245,158,11,0.15)] rounded-2xl max-w-lg w-full overflow-hidden"
      >
        <div className="bg-amber-500/10 p-6 flex flex-col items-center text-center border-b border-amber-500/20">
          <div className="w-12 h-12 bg-amber-500/20 rounded-full flex items-center justify-center mb-4 text-amber-400">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-amber-500 mb-1">Human Approval Required</h2>
          <p className="text-sm text-amber-200/70">
            The agent has been paused at a human gate. Review its intent before allowing execution to proceed.
          </p>
        </div>

        <div className="p-6">
          <div className="text-sm font-medium text-zinc-400 mb-2">Agent Summary & Intent:</div>
          <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 text-sm text-zinc-300 min-h-[100px] mb-6 whitespace-pre-wrap">
            {summary}
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => handleDecision("rejected")}
              disabled={isSubmitting}
              className="flex-1 flex items-center justify-center gap-2 bg-zinc-800 hover:bg-red-950 hover:text-red-400 text-zinc-300 py-2.5 rounded-lg border border-zinc-700 hover:border-red-900 transition-colors disabled:opacity-50"
            >
              <X className="w-4 h-4" /> Reject & Halt
            </button>
            <button
              onClick={() => handleDecision("approved")}
              disabled={isSubmitting}
              className="flex-1 flex items-center justify-center gap-2 bg-amber-500 hover:bg-amber-400 text-amber-950 font-semibold py-2.5 rounded-lg transition-colors disabled:opacity-50"
            >
              <Check className="w-4 h-4" /> Approve & Proceed
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
