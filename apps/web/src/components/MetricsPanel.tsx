import { BarChart3, Clock, Zap, TrendingUp } from "lucide-react";
import { Metrics } from "../types";

interface MetricsPanelProps {
  metrics: Metrics;
}

export function MetricsPanel({ metrics }: MetricsPanelProps) {
  const formatLatency = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const getLatencyColor = (ms: number) => {
    if (ms < 2000) return "text-green-600";
    if (ms < 5000) return "text-yellow-600";
    return "text-red-600";
  };

  const getTokenEfficiency = () => {
    if (metrics.latency_ms === 0) return 0;
    return Math.round((metrics.token_usage / metrics.latency_ms) * 1000);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 md:p-8">
      <div className="flex items-center gap-2 md:gap-3 mb-6">
        <BarChart3 className="w-5 h-5 md:w-6 md:h-6 text-blue-600" />
        <h2 className="text-xl md:text-2xl font-bold text-gray-900">
          Performance Metrics
        </h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
        <div className="bg-gray-50 rounded-lg p-4 md:p-5">
          <div className="flex items-center gap-2 mb-3">
            <Clock className="w-4 h-4 md:w-5 md:h-5 text-gray-600" />
            <span className="text-xs md:text-sm font-semibold text-gray-700">
              Total Latency
            </span>
          </div>
          <p
            className={`text-xl md:text-2xl font-bold ${getLatencyColor(
              metrics.latency_ms
            )}`}
          >
            {formatLatency(metrics.latency_ms)}
          </p>
          <p className="text-xs text-gray-500 mt-2">
            {metrics.latency_ms < 2000
              ? "Excellent"
              : metrics.latency_ms < 5000
              ? "Good"
              : "Needs optimization"}
          </p>
        </div>

        <div className="bg-gray-50 rounded-lg p-4 md:p-5">
          <div className="flex items-center gap-2 mb-3">
            <Zap className="w-4 h-4 md:w-5 md:h-5 text-gray-600" />
            <span className="text-xs md:text-sm font-semibold text-gray-700">
              Token Usage
            </span>
          </div>
          <p className="text-xl md:text-2xl font-bold text-blue-600">
            {metrics.token_usage.toLocaleString()}
          </p>
          <p className="text-xs text-gray-500 mt-2">Total tokens processed</p>
        </div>

        <div className="bg-gray-50 rounded-lg p-4 md:p-5">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-4 h-4 md:w-5 md:h-5 text-gray-600" />
            <span className="text-xs md:text-sm font-semibold text-gray-700">
              Efficiency
            </span>
          </div>
          <p className="text-xl md:text-2xl font-bold text-green-600">
            {getTokenEfficiency()}
          </p>
          <p className="text-xs text-gray-500 mt-2">Tokens/second</p>
        </div>

        <div className="bg-gray-50 rounded-lg p-4 md:p-5">
          <div className="flex items-center gap-2 mb-3">
            <BarChart3 className="w-4 h-4 md:w-5 md:h-5 text-gray-600" />
            <span className="text-xs md:text-sm font-semibold text-gray-700">
              Cost Estimate
            </span>
          </div>
          <p className="text-xl md:text-2xl font-bold text-purple-600">
            ${(metrics.token_usage * 0.00002).toFixed(4)}
          </p>
          <p className="text-xs text-gray-500 mt-2">Approx. processing cost</p>
        </div>
      </div>

      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-xs md:text-sm text-blue-800">
          <strong>Performance Insights:</strong> These metrics help track the
          efficiency and cost of AI processing. Lower latency and optimal token
          usage indicate better performance. The cost estimate is based on
          standard AI model pricing.
        </p>
      </div>
    </div>
  );
}
