import { useState } from "react";
import "./App.css";

function App() {
  const [requestText, setRequestText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!requestText.trim()) return;

    setIsLoading(true);
    try {
      const result = await fetch("/api/process", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ request_text: requestText }),
      });
      const data = await result.json();
      setResponse(data);
    } catch (error) {
      console.error("Error processing request:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
          Agentic Support Copilot
        </h1>

        <form onSubmit={handleSubmit} className="mb-8">
          <div className="mb-4">
            <label
              htmlFor="request"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Support Request
            </label>
            <textarea
              id="request"
              value={requestText}
              onChange={(e) => setRequestText(e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your support request here..."
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || !requestText.trim()}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isLoading ? "Processing..." : "Generate Answer"}
          </button>
        </form>

        {response && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-3">Answer</h2>
              <p className="text-gray-700 whitespace-pre-wrap">
                {response.answer}
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-3">Sources</h2>
              {response.sources?.length > 0 ? (
                <ul className="space-y-3">
                  {response.sources.map((source: any, index: number) => (
                    <li key={index} className="border-l-4 border-blue-500 pl-4">
                      <h3 className="font-medium">{source.title}</h3>
                      <p className="text-sm text-gray-600 mt-1">
                        {source.content}
                      </p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500">No sources were used.</p>
              )}
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-3">Agent Trace</h2>
              {response.trace?.length > 0 ? (
                <div className="space-y-3">
                  {response.trace.map((step: any, index: number) => (
                    <div
                      key={index}
                      className="border border-gray-200 rounded p-3"
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-medium">{step.agent_name}</h3>
                          <p className="text-sm text-gray-600">
                            {step.step_name}
                          </p>
                        </div>
                        <span className="text-sm text-gray-500">
                          {step.duration_ms}ms
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No trace information available.</p>
              )}
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-3">Metrics</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Latency</p>
                  <p className="text-lg font-medium">
                    {response.metrics?.latency_ms}ms
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Token Usage</p>
                  <p className="text-lg font-medium">
                    {response.metrics?.token_usage}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
