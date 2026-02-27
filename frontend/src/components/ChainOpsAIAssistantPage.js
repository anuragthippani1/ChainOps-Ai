import React from "react";
import ChatPanel from "./ChatPanel";

const ChainOpsAIAssistantPage = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          ChainOps AI Assistant
        </h1>
        <p className="mt-2 text-lg text-gray-600">
          Your AI-powered shipping intelligence partner
        </p>
      </div>

      {/* Chat Panel */}
      <div className="max-w-5xl mx-auto">
        <ChatPanel />
      </div>
    </div>
  );
};

export default ChainOpsAIAssistantPage;
