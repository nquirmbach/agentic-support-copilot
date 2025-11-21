import { useState } from "react";
import { Brain, AlertCircle, CheckCircle } from "lucide-react";
import { InputForm } from "./components/InputForm";
import { AnswerDisplay } from "./components/AnswerDisplay";
import { SourcesList } from "./components/SourcesList";
import { TraceTimeline } from "./components/TraceTimeline";
import { MetricsPanel } from "./components/MetricsPanel";
import { apiClient, ApiError } from "./services/api";
import { ProcessResponse } from "./types";
import "./App.css";

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<ProcessResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (requestText: string) => {
    setIsLoading(true);
    setError(null);
    setResponse(null);

    try {
      const result = await apiClient.processRequest({
        request_text: requestText,
      });
      setResponse(result);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
      console.error("Error processing request:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResponse(null);
    setError(null);
  };

  return (
    <div className="min-h-screen">
      <div className="max-w-5xl mx-auto px-4 md:px-6 py-8 md:py-12">
        {/* Header */}
        <div className="text-center mb-8 md:mb-12">
          <div className="flex items-center justify-center gap-2 md:gap-3 mb-4 md:mb-6">
            <Brain className="w-8 h-8 md:w-10 md:h-10 text-blue-600" />
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 tracking-tight">
              Agentic Support Copilot
            </h1>
          </div>
          <p className="text-lg md:text-xl text-gray-600 max-w-2xl md:max-w-3xl mx-auto leading-relaxed">
            Get intelligent, context-aware support responses powered by
            multi-agent AI processing
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-red-500 hover:text-red-700"
              >
                ×
              </button>
            </div>
          </div>
        )}

        {/* Input Form */}
        <div className="mb-8">
          <InputForm onSubmit={handleSubmit} isLoading={isLoading} />
        </div>

        {/* Results Display */}
        {response && (
          <div className="space-y-6">
            {/* Success Header */}
            <div className="flex items-center justify-between bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span className="text-sm font-medium text-green-800">
                  Response generated successfully
                </span>
              </div>
              <button
                onClick={handleReset}
                className="text-sm text-green-700 hover:text-green-900 underline"
              >
                Clear and start new request
              </button>
            </div>

            {/* Answer Display */}
            <AnswerDisplay
              answer={response.answer}
              isSafe={
                response.trace?.find((step) => step.agent_name === "GuardAgent")
                  ?.output?.is_safe
              }
              validationReasons={
                response.trace?.find((step) => step.agent_name === "GuardAgent")
                  ?.output?.issues
              }
            />

            {/* Sources and Metrics Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <SourcesList sources={response.sources} />
              <MetricsPanel metrics={response.metrics} />
            </div>

            {/* Trace Timeline */}
            <TraceTimeline trace={response.trace} />
          </div>
        )}

        {/* Footer */}
        <div className="mt-12 text-center text-sm text-gray-500">
          <p>
            Powered by Azure OpenAI • Multi-agent processing • Real-time
            knowledge retrieval
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
