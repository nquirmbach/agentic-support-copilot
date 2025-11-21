import { useState } from "react";
import { Send, Loader2 } from "lucide-react";

interface InputFormProps {
  onSubmit: (requestText: string) => void;
  isLoading: boolean;
}

export function InputForm({ onSubmit, isLoading }: InputFormProps) {
  const [requestText, setRequestText] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!requestText.trim() || isLoading) return;

    onSubmit(requestText);
    setRequestText("");
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 md:p-8"
    >
      <div className="mb-6">
        <label
          htmlFor="request"
          className="block text-sm font-semibold text-gray-900 mb-3"
        >
          Describe your support request
        </label>
        <textarea
          id="request"
          value={requestText}
          onChange={(e) => setRequestText(e.target.value)}
          rows={4}
          className="w-full px-3 md:px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-gray-900 placeholder-gray-500 transition-all duration-200 text-base"
          placeholder="I need help with..."
          disabled={isLoading}
        />
        <div className="mt-2 text-right">
          <span className="text-xs text-gray-500">
            {requestText.length}/1000 characters
          </span>
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading || !requestText.trim() || requestText.length > 1000}
        className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-3 font-medium text-base shadow-sm hover:shadow-md min-h-[48px]"
      >
        {isLoading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            <span className="hidden sm:inline">Processing...</span>
            <span className="sm:hidden">Processing</span>
          </>
        ) : (
          <>
            <Send className="w-5 h-5" />
            <span className="hidden sm:inline">Generate Answer</span>
            <span className="sm:hidden">Generate</span>
          </>
        )}
      </button>
    </form>
  );
}
