import { BookOpen, ExternalLink } from "lucide-react";
import { Source } from "../types";

interface SourcesListProps {
  sources: Source[];
}

export function SourcesList({ sources }: SourcesListProps) {
  if (!sources || sources.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center gap-2 mb-4">
          <BookOpen className="w-5 h-5 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">
            Knowledge Sources
          </h2>
        </div>
        <p className="text-gray-500 text-center py-4">
          No specific knowledge sources were referenced for this request.
        </p>
      </div>
    );
  }

  const getSimilarityColor = (score: number) => {
    if (score >= 0.8) return "bg-green-100 text-green-800";
    if (score >= 0.6) return "bg-yellow-100 text-yellow-800";
    return "bg-gray-100 text-gray-800";
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 md:p-8">
      <div className="flex items-center gap-2 md:gap-3 mb-6">
        <BookOpen className="w-5 h-5 md:w-6 md:h-6 text-blue-600" />
        <h2 className="text-xl md:text-2xl font-bold text-gray-900">
          Knowledge Sources ({sources.length})
        </h2>
      </div>

      <div className="space-y-3 md:space-y-4">
        {sources.map((source, index) => (
          <div
            key={source.id || index}
            className="border border-gray-200 rounded-lg p-4 md:p-5 hover:border-blue-300 hover:shadow-sm transition-all duration-200"
          >
            <div className="flex flex-col sm:flex-row sm:items-start justify-between mb-3 gap-2">
              <h3 className="font-semibold text-gray-900 flex-1 text-sm md:text-base">
                {source.title}
              </h3>
              <div className="flex items-center gap-2 sm:ml-4">
                <span
                  className={`inline-flex items-center px-2 md:px-3 py-1 rounded-full text-xs md:text-sm font-medium ${getSimilarityColor(
                    source.similarity_score
                  )}`}
                >
                  {Math.round(source.similarity_score * 100)}% match
                </span>
              </div>
            </div>

            <p className="text-xs md:text-sm text-gray-700 leading-relaxed">
              {source.content}
            </p>

            <div className="mt-3 md:mt-4 flex items-center gap-2 text-xs text-gray-500">
              <ExternalLink className="w-3 h-3" />
              <span>Source ID: {source.id}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-xs md:text-sm text-blue-800">
          <strong>Note:</strong> These knowledge sources were used to generate
          the response above. The similarity score indicates how relevant each
          source was to your request.
        </p>
      </div>
    </div>
  );
}
