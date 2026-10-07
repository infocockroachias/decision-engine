import { useState } from "react";

interface Option {
  id: string;
  text: string;
}

interface QuestionCardProps {
  questionNumber: number;
  totalQuestions: number;
  questionText: string;
  options: Option[];
  selectedOption: string | null;
  onSelect: (optionId: string) => void;
  onMarkForReview: () => void;
  isMarkedForReview: boolean;
  imageUrl?: string;
}

export default function QuestionCard({
  questionNumber,
  totalQuestions,
  questionText,
  options,
  selectedOption,
  onSelect,
  onMarkForReview,
  isMarkedForReview,
  imageUrl,
}: QuestionCardProps) {
  const [showExplanation, setShowExplanation] = useState(false);

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm" role="group" aria-label={`Question ${questionNumber} of ${totalQuestions}`}>
      {/* Question Header */}
      <div className="flex items-center justify-between mb-4">
        <span className="inline-flex items-center rounded-full bg-brand/10 px-3 py-1 text-sm font-semibold text-brand">
          Q.{questionNumber}/{totalQuestions}
        </span>
        <button
          onClick={onMarkForReview}
          className={`rounded-lg px-3 py-1 text-sm font-medium transition-all
            ${isMarkedForReview ? "bg-warning text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"}`}
          aria-label={isMarkedForReview ? "Unmark for review" : "Mark for review"}
          aria-pressed={isMarkedForReview}
        >
          {isMarkedForReview ? "★ Marked" : "☆ Review"}
        </button>
      </div>

      {/* Question Text */}
      <div className="mb-6">
        <p className="text-lg font-medium text-slate-900 leading-relaxed">{questionText}</p>
        {imageUrl && (
          <img
            src={imageUrl}
            alt="Question diagram"
            className="mt-3 max-h-48 rounded-lg border border-slate-200 object-contain"
          />
        )}
      </div>

      {/* Options */}
      <fieldset className="space-y-3">
        <legend className="sr-only">Answer options</legend>
        {options.map((option) => {
          const isSelected = selectedOption === option.id;
          return (
            <label
              key={option.id}
              className={`flex cursor-pointer items-start gap-3 rounded-lg border-2 p-4 transition-all hover:bg-slate-50
                ${isSelected ? "border-brand bg-brand/5" : "border-slate-200"}`}
            >
              <input
                type="radio"
                name={`question-${questionNumber}`}
                value={option.id}
                checked={isSelected}
                onChange={() => onSelect(option.id)}
                className="mt-0.5 h-4 w-4 text-brand focus:ring-brand"
                aria-label={`Option ${option.id}: ${option.text}`}
              />
              <span className="flex items-center gap-2">
                <span className={`inline-flex h-7 w-7 items-center justify-center rounded-full text-sm font-bold
                  ${isSelected ? "bg-brand text-white" : "bg-slate-200 text-slate-600"}`}>
                  {option.id}
                </span>
                <span className="text-slate-700">{option.text}</span>
              </span>
            </label>
          );
        })}
      </fieldset>

      {/* Clear Selection */}
      {selectedOption && (
        <button
          onClick={() => onSelect("")}
          className="mt-4 text-sm text-slate-500 hover:text-slate-700 underline"
        >
          Clear selection
        </button>
      )}
    </div>
  );
}