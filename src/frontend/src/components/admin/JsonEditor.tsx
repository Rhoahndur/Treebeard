import React, { useState, useEffect } from 'react';
import { clsx } from 'clsx';

/**
 * JsonEditor Component
 *
 * Simple JSON editor with syntax validation.
 * Used for editing rate structures and other JSON fields in plan forms.
 *
 * @example
 * <JsonEditor
 *   value={rateStructure}
 *   onChange={setRateStructure}
 *   label="Tiered Rates"
 * />
 */

export interface JsonEditorProps {
  /** JSON value (object or string) */
  value: any;
  /** Change handler - receives parsed object or null if invalid */
  onChange: (value: any) => void;
  /** Label for the editor */
  label?: string;
  /** Help text */
  helperText?: string;
  /** Height of the editor */
  height?: string;
  /** Placeholder text */
  placeholder?: string;
  /** Error message */
  error?: string;
}

/**
 * JsonEditor Component
 */
export const JsonEditor: React.FC<JsonEditorProps> = ({
  value,
  onChange,
  label,
  helperText,
  height = '200px',
  placeholder = 'Enter JSON...',
  error: externalError,
}) => {
  const [jsonString, setJsonString] = useState('');
  const [internalError, setInternalError] = useState<string | null>(null);
  const [focused, setFocused] = useState(false);

  // Initialize from value
  useEffect(() => {
    if (value) {
      try {
        const formatted = typeof value === 'string'
          ? JSON.stringify(JSON.parse(value), null, 2)
          : JSON.stringify(value, null, 2);
        setJsonString(formatted);
      } catch {
        setJsonString(typeof value === 'string' ? value : '');
      }
    } else {
      setJsonString('');
    }
  }, [value]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    setJsonString(newValue);

    // Validate JSON
    if (!newValue.trim()) {
      setInternalError(null);
      onChange(null);
      return;
    }

    try {
      const parsed = JSON.parse(newValue);
      setInternalError(null);
      onChange(parsed);
    } catch (err) {
      setInternalError('Invalid JSON syntax');
      onChange(null);
    }
  };

  const handleFormat = () => {
    try {
      const parsed = JSON.parse(jsonString);
      const formatted = JSON.stringify(parsed, null, 2);
      setJsonString(formatted);
      setInternalError(null);
      onChange(parsed);
    } catch {
      setInternalError('Cannot format invalid JSON');
    }
  };

  const displayError = externalError || internalError;

  return (
    <div>
      {/* Label */}
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}

      {/* Editor */}
      <div
        className={clsx(
          'relative rounded-lg border-2 transition-colors',
          displayError
            ? 'border-danger'
            : focused
            ? 'border-primary-600'
            : 'border-gray-300'
        )}
      >
        <textarea
          value={jsonString}
          onChange={handleChange}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder={placeholder}
          className={clsx(
            'w-full px-3 py-2 font-mono text-sm bg-gray-900 text-gray-100 rounded-lg',
            'focus:outline-none resize-none'
          )}
          style={{ height }}
          spellCheck={false}
        />

        {/* Format button */}
        <button
          type="button"
          onClick={handleFormat}
          className="absolute top-2 right-2 px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded hover:bg-gray-600 transition-colors"
          disabled={!jsonString.trim()}
        >
          Format
        </button>
      </div>

      {/* Helper text or error */}
      {displayError ? (
        <p className="mt-1 text-sm text-danger">{displayError}</p>
      ) : helperText ? (
        <p className="mt-1 text-sm text-gray-500">{helperText}</p>
      ) : null}

      {/* Syntax hints */}
      {!displayError && focused && (
        <div className="mt-2 p-2 bg-gray-50 rounded text-xs text-gray-600">
          <p className="font-medium mb-1">JSON Syntax Tips:</p>
          <ul className="list-disc list-inside space-y-0.5">
            <li>Use double quotes for strings: "key": "value"</li>
            <li>Numbers don't need quotes: "age": 25</li>
            <li>Arrays use brackets: [1, 2, 3]</li>
            <li>Objects use braces: {"{"} "key": "value" {"}"}</li>
          </ul>
        </div>
      )}
    </div>
  );
};
