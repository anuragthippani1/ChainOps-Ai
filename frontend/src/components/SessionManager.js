import React, { useState } from "react";
import { useDashboard } from "../context/DashboardContext";

const SessionManager = () => {
  const {
    currentSession,
    sessions,
    createSession,
    switchToSession,
    updateSession,
    deleteSession,
  } = useDashboard();

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingSession, setEditingSession] = useState(null);
  const [newSessionName, setNewSessionName] = useState("");
  const [newSessionDescription, setNewSessionDescription] = useState("");
  const [editSessionName, setEditSessionName] = useState("");
  const [editSessionDescription, setEditSessionDescription] = useState("");
  const [loading, setLoading] = useState(false);

  const handleCreateSession = async (e) => {
    e.preventDefault();
    if (!newSessionName.trim()) return;

    setLoading(true);
    try {
      await createSession(newSessionName.trim(), newSessionDescription.trim());
      setNewSessionName("");
      setNewSessionDescription("");
      setShowCreateModal(false);
    } catch (error) {
      console.error("Failed to create session:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSwitchSession = async (sessionId) => {
    setLoading(true);
    try {
      await switchToSession(sessionId);
    } catch (error) {
      console.error("Failed to switch session:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleEditSession = (session) => {
    setEditingSession(session);
    setEditSessionName(session.name);
    setEditSessionDescription(session.description || "");
    setShowEditModal(true);
  };

  const handleUpdateSession = async (e) => {
    e.preventDefault();
    if (!editSessionName.trim() || !editingSession) return;

    setLoading(true);
    try {
      await updateSession(editingSession.session_id, {
        name: editSessionName.trim(),
        description: editSessionDescription.trim(),
      });
      setShowEditModal(false);
      setEditingSession(null);
    } catch (error) {
      console.error("Failed to update session:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSession = async (sessionId) => {
    if (
      !window.confirm(
        "Are you sure you want to delete this session? This action cannot be undone."
      )
    ) {
      return;
    }

    setLoading(true);
    try {
      await deleteSession(sessionId);
    } catch (error) {
      console.error("Failed to delete session:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Session Manager</h3>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
        >
          + New Session
        </button>
      </div>

      {/* Current Session */}
      {currentSession && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-blue-900">Current Session</h4>
              <p className="text-blue-700">{currentSession.name}</p>
              {currentSession.description && (
                <p className="text-blue-600 text-sm">
                  {currentSession.description}
                </p>
              )}
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => handleEditSession(currentSession)}
                className="text-blue-600 hover:text-blue-800 text-sm"
              >
                Edit
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Sessions List */}
      <div className="space-y-2">
        {sessions.map((session) => (
          <div
            key={session.session_id}
            className={`p-3 rounded-md border ${
              currentSession?.session_id === session.session_id
                ? "bg-blue-50 border-blue-200"
                : "bg-gray-50 border-gray-200 hover:bg-gray-100"
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <h5 className="font-medium text-gray-900">{session.name}</h5>
                  {session.report_count > 0 && (
                    <span className="bg-gray-200 text-gray-700 px-2 py-1 rounded-full text-xs">
                      {session.report_count} reports
                    </span>
                  )}
                </div>
                {session.description && (
                  <p className="text-gray-600 text-sm">{session.description}</p>
                )}
                <p className="text-gray-500 text-xs">
                  Created: {new Date(session.created_at).toLocaleDateString()}
                </p>
              </div>
              <div className="flex space-x-2">
                {currentSession?.session_id !== session.session_id && (
                  <button
                    onClick={() => handleSwitchSession(session.session_id)}
                    disabled={loading}
                    className="text-blue-600 hover:text-blue-800 text-sm disabled:opacity-50"
                  >
                    Switch
                  </button>
                )}
                <button
                  onClick={() => handleEditSession(session)}
                  className="text-gray-600 hover:text-gray-800 text-sm"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDeleteSession(session.session_id)}
                  className="text-red-600 hover:text-red-800 text-sm"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Create Session Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Create New Session</h3>
            <form onSubmit={handleCreateSession}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Session Name
                </label>
                <input
                  type="text"
                  value={newSessionName}
                  onChange={(e) => setNewSessionName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter session name"
                  required
                />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description (Optional)
                </label>
                <textarea
                  value={newSessionDescription}
                  onChange={(e) => setNewSessionDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter session description"
                  rows={3}
                />
              </div>
              <div className="flex space-x-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md disabled:opacity-50"
                >
                  {loading ? "Creating..." : "Create Session"}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 py-2 px-4 rounded-md"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Session Modal */}
      {showEditModal && editingSession && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Edit Session</h3>
            <form onSubmit={handleUpdateSession}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Session Name
                </label>
                <input
                  type="text"
                  value={editSessionName}
                  onChange={(e) => setEditSessionName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter session name"
                  required
                />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description (Optional)
                </label>
                <textarea
                  value={editSessionDescription}
                  onChange={(e) => setEditSessionDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter session description"
                  rows={3}
                />
              </div>
              <div className="flex space-x-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md disabled:opacity-50"
                >
                  {loading ? "Updating..." : "Update Session"}
                </button>
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 py-2 px-4 rounded-md"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default SessionManager;
