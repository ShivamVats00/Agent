"use client";

import { useAgentStream } from "@/lib/useAgentStream";
import { DecisionTree } from "@/components/DecisionTree";
import { ToolCallLog } from "@/components/ToolCallLog";
import { ChatInterface } from "@/components/ChatInterface";
import { ApprovalModal } from "@/components/ApprovalModal";

export default function Home() {
  const { state, sendTask, disconnect } = useAgentStream();

  const handleSend = (message: string) => {
    sendTask(message, `thread-${Date.now()}`);
  };

  return (
    <main className="min-h-screen bg-zinc-950 p-4 md:p-6 lg:p-8 flex items-center justify-center">
      <div className="w-full max-w-7xl mx-auto h-[calc(100vh-4rem)] md:h-[calc(100vh-6rem)] relative grid grid-cols-1 lg:grid-cols-12 gap-6">

        <div className="lg:col-span-5 h-full">
          <ChatInterface state={state} onSend={handleSend} onDisconnect={disconnect} />
        </div>

        <div className="lg:col-span-7 h-full flex flex-col gap-6">
          <div className="flex-[3] min-h-0">
            <DecisionTree state={state} />
          </div>
          <div className="flex-[2] min-h-0">
            <ToolCallLog state={state} />
          </div>
        </div>
      </div>

      {state.requiresApproval && state.approvalSummary && (
        <ApprovalModal
          threadId="current-thread"
          summary={state.approvalSummary}
          onDecision={() => {}}
        />
      )}
    </main>
  );
}
