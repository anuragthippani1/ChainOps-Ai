import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  Bot,
  User,
  Loader,
  Upload,
  FilePlus2,
  Copy,
  CheckCircle,
  Download,
  Search,
  Globe,
  AlertTriangle,
  FileText,
  TrendingUp,
  X,
  Ship,
} from "lucide-react";
import { useDashboard } from "../context/DashboardContext";
import MultiPortRoutePlanner from "./MultiPortRoutePlanner";

const ChatPanel = () => {
  const {
    chatMessages,
    sendChatMessage,
    uploadShipmentData,
    generateCombinedReport,
  } = useDashboard();
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [copiedMessageId, setCopiedMessageId] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [showSearch, setShowSearch] = useState(false);
  const [routeForm, setRouteForm] = useState({
    from: "",
    to: "",
    cargo: "",
    priority: "cost",
  });
  const [showRouteForm, setShowRouteForm] = useState(false);
  const [routeAnalysis, setRouteAnalysis] = useState(null);
  const [showRoutePlanner, setShowRoutePlanner] = useState(false);
  const messagesEndRef = useRef(null);

  // Quick action templates
  const quickActions = [
    {
      icon: AlertTriangle,
      label: "Political Risks",
      query: "What are the political risks?",
    },
    {
      icon: TrendingUp,
      label: "Schedule Delays",
      query: "What are the schedule risks?",
    },
    {
      icon: FileText,
      label: "Combined Report",
      query: "Generate a combined report",
    },
    {
      icon: Globe,
      label: "High Risk Countries",
      query: "Which countries have high political risks?",
    },
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  // Quick action handler
  const handleQuickAction = (query) => {
    setInputMessage(query);
    // Auto-submit
    setTimeout(() => {
      handleSubmit({ preventDefault: () => {} });
    }, 100);
  };

  // Export chat history
  const exportChatHistory = () => {
    const chatText = chatMessages
      .map((msg) => {
        const time = new Date(msg.timestamp).toLocaleString();
        const sender = msg.type === "user" ? "You" : "ChainOps AI Assistant";
        return `[${time}] ${sender}:\n${msg.content}\n`;
      })
      .join("\n---\n\n");

    const blob = new Blob([chatText], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `chainops-ai-chat-${
      new Date().toISOString().split("T")[0]
    }.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Filter messages by search query (recalculates when chatMessages or searchQuery changes)
  const filteredMessages = React.useMemo(() => {
    if (!searchQuery.trim()) return chatMessages;
    return chatMessages.filter((msg) =>
      msg.content.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [chatMessages, searchQuery]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const message = inputMessage.toLowerCase();

    // Check if user wants route analysis
    if (
      message.includes("route") ||
      message.includes("shipping") ||
      message.includes("from") ||
      message.includes("to")
    ) {
      setShowRouteForm(true);
      setInputMessage("");
      return;
    }

    setIsLoading(true);
    setIsTyping(true);

    // Simulate typing delay
    setTimeout(async () => {
      await sendChatMessage(inputMessage);
      setInputMessage("");
      setIsLoading(false);
      setIsTyping(false);
    }, 1000);
  };

  const handleRouteSubmit = async (e) => {
    e.preventDefault();
    if (!routeForm.from || !routeForm.to) return;

    setIsLoading(true);
    setIsTyping(true);

    const routeQuery = `Route from ${routeForm.from} to ${routeForm.to} with ${
      routeForm.cargo || "general cargo"
    } (priority: ${routeForm.priority})`;

    setTimeout(async () => {
      await sendChatMessage(routeQuery);

      // Generate comprehensive route analysis
      const analysis = generateRouteAnalysis(routeForm);
      setRouteAnalysis(analysis);

      setIsLoading(false);
      setIsTyping(false);
      setShowRouteForm(false);
      setRouteForm({ from: "", to: "", cargo: "", priority: "cost" });
    }, 2000);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      setIsLoading(true);
      const text = await file.text();
      const json = JSON.parse(text);
      const dataArray = Array.isArray(json) ? json : json.data || [];
      await uploadShipmentData(dataArray);
      // Assuming setChatMessages is available from useDashboard context or passed as prop
      // For now, we'll simulate an update to show the message
      // In a real app, you'd update the context state here
      // setChatMessages(prev => [...prev, { id: Date.now()+2, type: 'bot', content: `Uploaded ${dataArray.length} shipment records and refreshed dashboard.`, timestamp: new Date().toISOString() }]);
    } catch (err) {
      // Assuming setChatMessages is available from useDashboard context or passed as prop
      // For now, we'll simulate an update to show the message
      // setChatMessages(prev => [...prev, { id: Date.now()+3, type: 'bot', content: 'Upload failed. Ensure valid JSON array of shipments.', timestamp: new Date().toISOString() }]);
    } finally {
      setIsLoading(false);
      e.target.value = "";
    }
  };

  const handleGenerateCombined = async () => {
    try {
      setIsLoading(true);
      await generateCombinedReport();
      // Assuming setChatMessages is available from useDashboard context or passed as prop
      // For now, we'll simulate an update to show the message
      // setChatMessages(prev => [...prev, { id: Date.now()+4, type: 'bot', content: `Combined report generated: ${res.report?.report_id}`, timestamp: new Date().toISOString(), data: res }]);
    } catch (e) {
      // Assuming setChatMessages is available from useDashboard context or passed as prop
      // For now, we'll simulate an update to show the message
      // setChatMessages(prev => [...prev, { id: Date.now()+5, type: 'bot', content: 'Failed to generate combined report.', timestamp: new Date().toISOString() }]);
    } finally {
      setIsLoading(false);
    }
  };

  const quickQuestions = [
    "What are the political risks?",
    "Which equipment has delivery delays?",
    "Show me the risk summary",
    "Generate a comprehensive report",
    "Route from Shanghai to Los Angeles",
    "Shipping analysis Singapore to Rotterdam",
  ];

  const handleQuickQuestion = (question) => {
    setInputMessage(question);
  };

  const copyMessage = (messageId, content) => {
    navigator.clipboard.writeText(content);
    setCopiedMessageId(messageId);
    setTimeout(() => setCopiedMessageId(null), 2000);
  };

  const generateRouteAnalysis = (form) => {
    const { from, to, cargo, priority } = form;

    // Mock comprehensive route analysis
    const analysis = {
      route: `${from} → ${to}`,
      cargo: cargo || "General Cargo",
      priority: priority,
      distance: Math.floor(Math.random() * 5000) + 3000, // nautical miles
      transitTime: Math.floor(Math.random() * 20) + 10, // days
      politicalRisk: Math.floor(Math.random() * 3) + 1, // 1-4
      weatherRisk: Math.floor(Math.random() * 3) + 2, // 2-5
      piracyRisk: Math.floor(Math.random() * 2) + 1, // 1-3
      portCongestion: Math.floor(Math.random() * 3) + 2, // 2-5
      visibility: Math.floor(Math.random() * 5) + 5, // 5-10 km
      windSpeed: Math.floor(Math.random() * 20) + 10, // knots
      seaTemperature: Math.floor(Math.random() * 15) + 10, // celsius
      waveHeight: (Math.random() * 3 + 1).toFixed(1), // meters
      fuelCost: Math.floor(Math.random() * 500000) + 200000, // USD
      totalCost: Math.floor(Math.random() * 800000) + 400000, // USD
      alternativeRoutes: [
        { name: "Direct Route", time: "12 days", cost: "High", risk: "Medium" },
        {
          name: "Via Panama Canal",
          time: "18 days",
          cost: "Medium",
          risk: "Low",
        },
        { name: "Via Suez Canal", time: "22 days", cost: "Low", risk: "High" },
      ],
      weatherForecast: [
        { day: 1, condition: "Clear", wind: "15 kts", waves: "1.2m" },
        { day: 2, condition: "Partly Cloudy", wind: "18 kts", waves: "1.5m" },
        { day: 3, condition: "Storm", wind: "25 kts", waves: "2.8m" },
        { day: 4, condition: "Clear", wind: "12 kts", waves: "1.0m" },
      ],
      safetyPrecautions: [
        "Monitor weather forecasts continuously",
        "Maintain communication with coast guard",
        "Follow ISPS security protocols",
        "Ensure cargo is properly secured",
        "Have emergency response plans ready",
        "Regular equipment maintenance checks",
      ],
    };

    return analysis;
  };

  // If showing route planner, render it instead of chat
  if (showRoutePlanner) {
    return (
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-sm border border-gray-200 dark:border-gray-800">
        <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
            <Ship className="h-5 w-5 mr-2 text-blue-600 dark:text-blue-400" />
            Multi-Port Route Planner
          </h3>
          <button
            onClick={() => setShowRoutePlanner(false)}
            className="inline-flex items-center px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded transition-colors"
          >
            <X className="h-4 w-4 mr-1" /> Close
          </button>
        </div>
        <div
          className="overflow-y-auto"
          style={{ maxHeight: "calc(100vh - 200px)" }}
        >
          <MultiPortRoutePlanner />
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-[600px] flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              ChainOps AI Assistant
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Ask me about supply chain risks
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowRoutePlanner(true)}
              className="inline-flex items-center px-2 py-1 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
              title="Route Planner"
            >
              <Ship className="h-3 w-3 mr-1" /> Route Planner
            </button>
            <button
              onClick={() => setShowSearch(!showSearch)}
              className="inline-flex items-center px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded transition-colors"
              title="Search chat"
            >
              <Search className="h-3 w-3 mr-1" /> Search
            </button>
            <button
              onClick={exportChatHistory}
              className="inline-flex items-center px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded transition-colors"
              title="Export chat"
              disabled={chatMessages.length === 0}
            >
              <Download className="h-3 w-3 mr-1" /> Export
            </button>
            <label className="inline-flex items-center px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded cursor-pointer transition-colors">
              <Upload className="h-3 w-3 mr-1" /> Upload
              <input
                type="file"
                accept="application/json"
                className="hidden"
                onChange={handleFileUpload}
              />
            </label>
            <button
              onClick={handleGenerateCombined}
              className="inline-flex items-center px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              <FilePlus2 className="h-3 w-3 mr-1" /> Report
            </button>
          </div>
        </div>

        {/* Search Bar */}
        {showSearch && (
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search messages..."
              className="w-full pl-10 pr-10 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
        )}

        {/* Quick Action Buttons */}
        {chatMessages.length === 0 && !searchQuery && (
          <div className="grid grid-cols-2 gap-2 mt-3">
            {quickActions.map((action, index) => {
              const Icon = action.icon;
              return (
                <button
                  key={index}
                  onClick={() => handleQuickAction(action.query)}
                  className="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-lg text-sm font-medium transition-colors"
                >
                  <Icon className="h-4 w-4" />
                  {action.label}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Route Form Modal */}
      {showRouteForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-96 max-w-md mx-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              🚢 Route Analysis Request
            </h3>
            <form onSubmit={handleRouteSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  From Port/City
                </label>
                <input
                  type="text"
                  value={routeForm.from}
                  onChange={(e) =>
                    setRouteForm({ ...routeForm, from: e.target.value })
                  }
                  placeholder="e.g., Shanghai, Singapore, Rotterdam"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  To Port/City
                </label>
                <input
                  type="text"
                  value={routeForm.to}
                  onChange={(e) =>
                    setRouteForm({ ...routeForm, to: e.target.value })
                  }
                  placeholder="e.g., Los Angeles, Hamburg, Dubai"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Cargo Type
                </label>
                <select
                  value={routeForm.cargo}
                  onChange={(e) =>
                    setRouteForm({ ...routeForm, cargo: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">General Cargo</option>
                  <option value="Container">Container</option>
                  <option value="Bulk">Bulk Cargo</option>
                  <option value="Liquid">Liquid Cargo</option>
                  <option value="Dangerous">Dangerous Goods</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Priority
                </label>
                <select
                  value={routeForm.priority}
                  onChange={(e) =>
                    setRouteForm({ ...routeForm, priority: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="cost">Cost Optimization</option>
                  <option value="speed">Speed Priority</option>
                  <option value="safety">Safety First</option>
                  <option value="balanced">Balanced</option>
                </select>
              </div>
              <div className="flex gap-2 pt-4">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                  Analyze Route
                </button>
                <button
                  type="button"
                  onClick={() => setShowRouteForm(false)}
                  className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {filteredMessages.length === 0 && !searchQuery ? (
          <div className="text-center text-gray-500">
            <Bot className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p className="text-sm">
              Start a conversation about supply chain risks
            </p>
            <div className="mt-4 space-y-2">
              <p className="text-xs text-gray-400">Quick questions:</p>
              {quickQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickQuestion(question)}
                  className="block w-full text-left text-xs bg-gray-50 hover:bg-gray-100 p-2 rounded transition-colors"
                >
                  {question}
                </button>
              ))}
              <button
                onClick={() => setShowRouteForm(true)}
                className="block w-full text-left text-xs bg-blue-50 hover:bg-blue-100 p-2 rounded transition-colors text-blue-700"
              >
                🚢 Analyze Shipping Route
              </button>
            </div>
          </div>
        ) : searchQuery && filteredMessages.length === 0 ? (
          <div className="text-center text-gray-500">
            <Search className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p className="text-sm">No messages found for "{searchQuery}"</p>
          </div>
        ) : (
          filteredMessages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.type === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-xs lg:max-w-2xl px-4 py-3 rounded-lg ${
                  message.type === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                }`}
              >
                <div className="flex items-start space-x-2">
                  {message.type === "bot" && (
                    <Bot className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  )}
                  {message.type === "user" && (
                    <User className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  )}
                  <div className="flex-1 min-w-0">
                    <div className="whitespace-pre-wrap break-words text-sm overflow-wrap-anywhere">
                      {message.content}
                    </div>
                  </div>
                  <button
                    onClick={() => copyMessage(message.id, message.content)}
                    className="opacity-50 hover:opacity-100 transition-opacity"
                  >
                    {copiedMessageId === message.id ? (
                      <CheckCircle className="h-3 w-3 text-green-600" />
                    ) : (
                      <Copy className="h-3 w-3" />
                    )}
                  </button>
                </div>
                <p className="text-xs opacity-70 mt-1">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))
        )}

        {/* Route Analysis Display */}
        {routeAnalysis && (
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-900 mb-3">
              🚢 Route Analysis: {routeAnalysis.route}
            </h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Distance:</span>
                  <span className="font-medium">
                    {routeAnalysis.distance} nm
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Transit Time:</span>
                  <span className="font-medium">
                    {routeAnalysis.transitTime} days
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Political Risk:</span>
                  <span
                    className={`font-medium ${
                      routeAnalysis.politicalRisk <= 2
                        ? "text-green-600"
                        : routeAnalysis.politicalRisk <= 3
                        ? "text-yellow-600"
                        : "text-red-600"
                    }`}
                  >
                    {routeAnalysis.politicalRisk}/5
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Weather Risk:</span>
                  <span
                    className={`font-medium ${
                      routeAnalysis.weatherRisk <= 2
                        ? "text-green-600"
                        : routeAnalysis.weatherRisk <= 3
                        ? "text-yellow-600"
                        : "text-red-600"
                    }`}
                  >
                    {routeAnalysis.weatherRisk}/5
                  </span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Visibility:</span>
                  <span className="font-medium">
                    {routeAnalysis.visibility} km
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Wind Speed:</span>
                  <span className="font-medium">
                    {routeAnalysis.windSpeed} kts
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Wave Height:</span>
                  <span className="font-medium">
                    {routeAnalysis.waveHeight}m
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Sea Temp:</span>
                  <span className="font-medium">
                    {routeAnalysis.seaTemperature}°C
                  </span>
                </div>
              </div>
            </div>
            <div className="mt-4 pt-3 border-t border-blue-200">
              <p className="text-sm text-blue-800">
                💰 Total Cost: ${routeAnalysis.totalCost.toLocaleString()} | 🛡️
                Safety Score: {Math.floor(Math.random() * 2) + 8}/10
              </p>
            </div>
          </div>
        )}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-900 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
              <div className="flex items-center space-x-2">
                <Bot className="h-4 w-4" />
                {isTyping ? (
                  <>
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      ></div>
                    </div>
                    <span className="text-sm">Typing...</span>
                  </>
                ) : (
                  <>
                    <Loader className="h-4 w-4 animate-spin" />
                    <span className="text-sm">Analyzing...</span>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 p-4">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask about routes, risks, or type 'route' for shipping analysis..."
            className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatPanel;
