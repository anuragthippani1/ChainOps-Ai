import React from 'react';
import { useDashboard } from '../context/DashboardContext';
import { Brain, Clock, User, Bot, Activity } from 'lucide-react';

const ThinkingLogs = () => {
  const { chatMessages } = useDashboard();

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getMessageTypeIcon = (type) => {
    switch (type) {
      case 'user':
        return <User className="h-4 w-4" />;
      case 'bot':
        return <Bot className="h-4 w-4" />;
      default:
        return <Activity className="h-4 w-4" />;
    }
  };

  const getMessageTypeColor = (type) => {
    switch (type) {
      case 'user':
        return 'bg-blue-100 text-blue-800';
      case 'bot':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <Brain className="h-8 w-8 mr-3 text-purple-600" />
          Thinking Logs
        </h1>
        <p className="mt-2 text-gray-600">Real-time AI agent reasoning and decision-making process</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Activity className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Interactions</p>
              <p className="text-2xl font-semibold text-gray-900">{chatMessages.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <User className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">User Queries</p>
              <p className="text-2xl font-semibold text-gray-900">
                {chatMessages.filter(m => m.type === 'user').length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Bot className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">AI Responses</p>
              <p className="text-2xl font-semibold text-gray-900">
                {chatMessages.filter(m => m.type === 'bot').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Messages List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Conversation History</h3>
          <p className="text-sm text-gray-600">Chronological log of all AI agent interactions</p>
        </div>

        {chatMessages.length === 0 ? (
          <div className="text-center py-12">
            <Brain className="h-12 w-12 mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Thinking Logs Yet</h3>
            <p className="text-gray-500">Start a conversation with the AI assistant to see thinking logs here.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {chatMessages.map((message, index) => (
              <div key={message.id} className="p-6 hover:bg-gray-50">
                <div className="flex items-start space-x-4">
                  {/* Message Type Icon */}
                  <div className={`flex-shrink-0 p-2 rounded-full ${getMessageTypeColor(message.type)}`}>
                    {getMessageTypeIcon(message.type)}
                  </div>

                  {/* Message Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-gray-900">
                          {message.type === 'user' ? 'User Query' : 'AI Response'}
                        </span>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getMessageTypeColor(message.type)}`}>
                          {message.type.toUpperCase()}
                        </span>
                      </div>
                      <div className="flex items-center text-sm text-gray-500">
                        <Clock className="h-4 w-4 mr-1" />
                        {formatTimestamp(message.timestamp)}
                      </div>
                    </div>

                    {/* Message Text */}
                    <div className="text-sm text-gray-900 mb-3">
                      {message.content}
                    </div>

                    {/* Additional Data */}
                    {message.data && (
                      <div className="bg-gray-50 rounded-lg p-4">
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Response Data:</h4>
                        <div className="text-sm text-gray-600 space-y-1">
                          {message.data.type && (
                            <p><span className="font-medium">Type:</span> {message.data.type}</p>
                          )}
                          {message.data.session_id && (
                            <p><span className="font-medium">Session:</span> {message.data.session_id}</p>
                          )}
                          {message.data.report && (
                            <div>
                              <p className="font-medium">Report Generated:</p>
                              <ul className="ml-4 space-y-1">
                                <li><span className="font-medium">ID:</span> {message.data.report.report_id}</li>
                                <li><span className="font-medium">Type:</span> {message.data.report.report_type}</li>
                                <li><span className="font-medium">Title:</span> {message.data.report.title}</li>
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Message Metadata */}
                    <div className="mt-3 flex items-center text-xs text-gray-500">
                      <span>Message ID: {message.id}</span>
                      <span className="mx-2">•</span>
                      <span>Timestamp: {message.timestamp}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ThinkingLogs;
