import React, { useState } from 'react';
import { Save, Share2, RotateCcw } from 'lucide-react';
import { Button } from '@/components/design-system';
import type { ScenarioParams } from '@/hooks/useScenario';

export interface ScenarioBuilderProps {
  scenario: ScenarioParams;
  onUpdate: (params: Partial<ScenarioParams>) => void;
  onReset: () => void;
  onSave: (name: string) => void;
  onShare: () => string;
}

export const ScenarioBuilder: React.FC<ScenarioBuilderProps> = ({
  scenario,
  onUpdate,
  onReset,
  onSave,
  onShare,
}) => {
  const [scenarioName, setScenarioName] = useState('');
  const [showSave, setShowSave] = useState(false);
  const [showShareUrl, setShowShareUrl] = useState(false);
  const [shareUrl, setShareUrl] = useState('');

  const handleSave = () => {
    if (scenarioName.trim()) {
      onSave(scenarioName.trim());
      setScenarioName('');
      setShowSave(false);
    }
  };

  const handleShare = () => {
    const url = onShare();
    setShareUrl(url);
    setShowShareUrl(true);
    navigator.clipboard.writeText(url);
  };

  return (
    <div className="bg-white rounded-lg shadow-card p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Scenario Builder</h2>
      <p className="text-sm text-gray-600 mb-6">
        Adjust parameters to see how different scenarios affect your recommendations
      </p>

      <div className="space-y-6">
        {/* Usage Adjustment */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Usage Adjustment: {scenario.usageAdjustment > 0 ? '+' : ''}
            {scenario.usageAdjustment}%
          </label>
          <input
            type="range"
            min="-50"
            max="50"
            value={scenario.usageAdjustment}
            onChange={(e) =>
              onUpdate({ usageAdjustment: Number(e.target.value) })
            }
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>-50%</span>
            <span>0%</span>
            <span>+50%</span>
          </div>
        </div>

        {/* Cost Priority */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Cost Priority: {scenario.costPriority}%
          </label>
          <input
            type="range"
            min="0"
            max="100"
            value={scenario.costPriority}
            onChange={(e) => onUpdate({ costPriority: Number(e.target.value) })}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Low</span>
            <span>Medium</span>
            <span>High</span>
          </div>
        </div>

        {/* Renewable Priority */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Renewable Priority: {scenario.renewablePriority}%
          </label>
          <input
            type="range"
            min="0"
            max="100"
            value={scenario.renewablePriority}
            onChange={(e) =>
              onUpdate({ renewablePriority: Number(e.target.value) })
            }
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-green-600"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Low</span>
            <span>Medium</span>
            <span>High</span>
          </div>
        </div>

        {/* Flexibility Priority */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Flexibility Priority: {scenario.flexibilityPriority}%
          </label>
          <input
            type="range"
            min="0"
            max="100"
            value={scenario.flexibilityPriority}
            onChange={(e) =>
              onUpdate({ flexibilityPriority: Number(e.target.value) })
            }
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Low</span>
            <span>Medium</span>
            <span>High</span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="mt-6 pt-6 border-t border-gray-200 flex flex-wrap gap-3">
        <Button variant="primary" onClick={() => setShowSave(true)}>
          <Save className="w-4 h-4 mr-2" />
          Save Scenario
        </Button>
        <Button variant="secondary" onClick={handleShare}>
          <Share2 className="w-4 h-4 mr-2" />
          Share
        </Button>
        <Button variant="outline" onClick={onReset}>
          <RotateCcw className="w-4 h-4 mr-2" />
          Reset
        </Button>
      </div>

      {/* Save Modal */}
      {showSave && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <input
            type="text"
            value={scenarioName}
            onChange={(e) => setScenarioName(e.target.value)}
            placeholder="Scenario name..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-2"
          />
          <div className="flex gap-2">
            <Button variant="primary" size="sm" onClick={handleSave}>
              Save
            </Button>
            <Button variant="outline" size="sm" onClick={() => setShowSave(false)}>
              Cancel
            </Button>
          </div>
        </div>
      )}

      {/* Share URL */}
      {showShareUrl && (
        <div className="mt-4 p-4 bg-green-50 rounded-lg">
          <p className="text-sm text-green-800 mb-2">
            URL copied to clipboard!
          </p>
          <input
            type="text"
            value={shareUrl}
            readOnly
            className="w-full px-3 py-2 border border-green-300 rounded-lg text-sm"
          />
        </div>
      )}
    </div>
  );
};

ScenarioBuilder.displayName = 'ScenarioBuilder';
