import { Activity, Clock, ChevronDown, ChevronRight } from "lucide-react";
import { useState } from "react";
import { AgentStep } from "../types";

interface TraceTimelineProps {
  trace: AgentStep[];
}

export function TraceTimeline({ trace }: TraceTimelineProps) {
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set());

  if (!trace || trace.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center gap-2 mb-4">
          <Activity className="w-5 h-5 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">Agent Trace</h2>
        </div>
        <p className="text-gray-500 text-center py-4">
          No trace information available.
        </p>
      </div>
    );
  }

  const toggleStep = (index: number) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedSteps(newExpanded);
  };

  const getAgentColor = (agentName: string) => {
    const colors: Record<string, string> = {
      ClassifierAgent: "bg-purple-100 text-purple-800 border-purple-200",
      RetrieverAgent: "bg-blue-100 text-blue-800 border-blue-200",
      WriterAgent: "bg-green-100 text-green-800 border-green-200",
      GuardAgent: "bg-yellow-100 text-yellow-800 border-yellow-200",
      LoggerAgent: "bg-gray-100 text-gray-800 border-gray-200",
    };
    return colors[agentName] || "bg-gray-100 text-gray-800 border-gray-200";
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const totalDuration = trace.reduce((sum, step) => sum + step.duration_ms, 0);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 md:p-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
        <div className="flex items-center gap-2 md:gap-3">
          <Activity className="w-5 h-5 md:w-6 md:h-6 text-blue-600" />
          <h2 className="text-xl md:text-2xl font-bold text-gray-900">
            Agent Trace
          </h2>
        </div>
        <div className="flex items-center gap-4 md:gap-6 text-xs md:text-sm text-gray-600">
          <div className="flex items-center gap-1 md:gap-2">
            <Clock className="w-3 h-3 md:w-4 md:h-4" />
            <span>Total: {formatDuration(totalDuration)}</span>
          </div>
          <span>{trace.length} steps</span>
        </div>
      </div>

      <div className="space-y-3">
        {trace.map((step, index) => (
          <div
            key={index}
            className="border border-gray-200 rounded-lg overflow-hidden"
          >
            <button
              onClick={() => toggleStep(index)}
              className="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors duration-200 flex items-center justify-between"
            >
              <div className="flex items-center gap-3">
                {expandedSteps.has(index) ? (
                  <ChevronDown className="w-4 h-4 text-gray-500" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-gray-500" />
                )}

                <div className="flex items-center gap-2">
                  <span
                    className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium border ${getAgentColor(
                      step.agent_name
                    )}`}
                  >
                    {step.agent_name.replace("Agent", "")}
                  </span>
                  <span className="text-sm font-medium text-gray-900">
                    {step.step_name}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-3 text-sm text-gray-600">
                <span className="font-medium">
                  {formatDuration(step.duration_ms)}
                </span>
                <span>{formatTimestamp(step.timestamp)}</span>
              </div>
            </button>

            {expandedSteps.has(index) && (
              <div className="px-4 py-3 border-t border-gray-200 bg-white">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 md:gap-4">
                  <div>
                    <h4 className="text-xs md:text-sm font-medium text-gray-700 mb-2">
                      Input
                    </h4>
                    <pre className="text-xs bg-gray-50 p-2 rounded border overflow-auto max-h-32 overflow-x-auto">
                      {JSON.stringify(step.input, null, 2)}
                    </pre>
                  </div>
                  <div>
                    <h4 className="text-xs md:text-sm font-medium text-gray-700 mb-2">
                      Output
                    </h4>
                    <pre className="text-xs bg-gray-50 p-2 rounded border overflow-auto max-h-32 overflow-x-auto">
                      {JSON.stringify(step.output, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
        <p className="text-xs md:text-sm text-gray-700">
          <strong>Trace Information:</strong> This timeline shows each step in
          the AI agent pipeline. Click on any step to see detailed input/output
          data. The duration shows how long each agent took to complete its
          task.
        </p>
      </div>
    </div>
  );
}
