import React from "react";
import SessionManager from "./SessionManager";

const SessionManagerPage = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Session Manager</h1>
        <p className="mt-2 text-lg text-gray-600">
          Manage your analysis sessions and track your work
        </p>
      </div>

      {/* Session Manager Component */}
      <SessionManager />
    </div>
  );
};

export default SessionManagerPage;

