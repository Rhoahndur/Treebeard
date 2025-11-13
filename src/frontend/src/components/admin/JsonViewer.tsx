import React, { useState } from 'react';

/**
 * JsonViewer Component
 *
 * Displays JSON data in a formatted, collapsible tree view.
 * Used for viewing audit log details and other structured data.
 *
 * @example
 * <JsonViewer data={{ user_id: '123', action: 'update' }} />
 */

export interface JsonViewerProps {
  /** JSON data to display */
  data: any;
  /** Initial expanded state */
  defaultExpanded?: boolean;
  /** Maximum height before scrolling */
  maxHeight?: string;
}

/**
 * JsonViewer Component
 */
export const JsonViewer: React.FC<JsonViewerProps> = ({
  data,
  defaultExpanded = true,
  maxHeight = '400px',
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const jsonString = JSON.stringify(data, null, 2);
    navigator.clipboard.writeText(jsonString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const jsonString = JSON.stringify(data, null, 2);

  return (
    <div className="bg-gray-900 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        <span className="text-xs font-medium text-gray-400 uppercase">JSON Data</span>
        <button
          onClick={handleCopy}
          className="text-xs text-gray-400 hover:text-white transition-colors flex items-center space-x-1"
          aria-label="Copy JSON"
        >
          {copied ? (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span>Copied!</span>
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Content */}
      <div
        className="overflow-auto p-4"
        style={{ maxHeight }}
      >
        <pre className="text-sm text-gray-300 font-mono">
          <code>{jsonString}</code>
        </pre>
      </div>
    </div>
  );
};

/**
 * CollapsibleJsonViewer Component
 *
 * Enhanced version with collapsible tree structure for nested objects
 */
interface CollapsibleJsonProps {
  data: any;
  level?: number;
}

export const CollapsibleJsonViewer: React.FC<CollapsibleJsonProps> = ({
  data,
  level = 0,
}) => {
  const [expanded, setExpanded] = useState(level < 2);

  const indent = level * 16;

  if (data === null) {
    return <span className="text-purple-400">null</span>;
  }

  if (typeof data === 'boolean') {
    return <span className="text-yellow-400">{data.toString()}</span>;
  }

  if (typeof data === 'number') {
    return <span className="text-blue-400">{data}</span>;
  }

  if (typeof data === 'string') {
    return <span className="text-green-400">"{data}"</span>;
  }

  if (Array.isArray(data)) {
    if (data.length === 0) {
      return <span className="text-gray-400">[]</span>;
    }

    return (
      <div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-gray-400 hover:text-white transition-colors"
        >
          {expanded ? '▼' : '▶'} Array[{data.length}]
        </button>
        {expanded && (
          <div className="ml-4">
            {data.map((item, index) => (
              <div key={index} className="my-1">
                <span className="text-gray-500">{index}: </span>
                <CollapsibleJsonViewer data={item} level={level + 1} />
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  if (typeof data === 'object') {
    const keys = Object.keys(data);

    if (keys.length === 0) {
      return <span className="text-gray-400">{'{}'}</span>;
    }

    return (
      <div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-gray-400 hover:text-white transition-colors"
        >
          {expanded ? '▼' : '▶'} Object
        </button>
        {expanded && (
          <div className="ml-4">
            {keys.map((key) => (
              <div key={key} className="my-1">
                <span className="text-cyan-400">"{key}"</span>
                <span className="text-gray-500">: </span>
                <CollapsibleJsonViewer data={data[key]} level={level + 1} />
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  return <span className="text-gray-400">{String(data)}</span>;
};
