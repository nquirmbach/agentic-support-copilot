import { MessageCircle, CheckCircle, AlertTriangle } from "lucide-react";

interface AnswerDisplayProps {
  answer: string;
  isSafe?: boolean;
  validationReasons?: string[];
}

export function AnswerDisplay({
  answer,
  isSafe,
  validationReasons,
}: AnswerDisplayProps) {
  const getStatusIcon = () => {
    if (isSafe === false) {
      return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
    }
    return <CheckCircle className="w-5 h-5 text-green-500" />;
  };

  const getStatusText = () => {
    if (isSafe === false) {
      return "Response completed with warnings";
    }
    return "Response validated and safe";
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 md:p-8">
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 mb-6">
        <div className="flex items-center gap-3">
          <MessageCircle className="w-5 h-5 md:w-6 md:h-6 text-blue-600" />
          <h2 className="text-xl md:text-2xl font-bold text-gray-900">
            AI Response
          </h2>
        </div>
        <div className="flex items-center gap-2 sm:ml-auto">
          {getStatusIcon()}
          <span className="text-xs sm:text-sm text-gray-600">
            {getStatusText()}
          </span>
        </div>
      </div>

      <div className="prose prose-base md:prose-lg max-w-none">
        <p className="text-gray-800 whitespace-pre-wrap leading-relaxed text-sm md:text-base">
          {answer}
        </p>
      </div>

      {isSafe === false &&
        validationReasons &&
        validationReasons.length > 0 && (
          <div className="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <div className="flex items-start gap-2 mb-3">
              <AlertTriangle className="w-4 h-4 md:w-5 md:h-5 text-amber-600 mt-0.5" />
              <span className="text-sm font-semibold text-amber-900">
                Validation Warnings
              </span>
            </div>
            <ul className="text-sm text-amber-800 space-y-2">
              {validationReasons.map((reason, index) => (
                <li key={index}>• {reason}</li>
              ))}
            </ul>
          </div>
        )}
    </div>
  );
}
