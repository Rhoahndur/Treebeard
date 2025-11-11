import React from 'react';
import { Trash2 } from 'lucide-react';
import type { SavedScenario } from '@/hooks/useScenario';
import { Button } from '@/components/design-system';

export interface ScenarioComparisonProps {
  scenarios: SavedScenario[];
  onLoad: (id: string) => void;
  onDelete: (id: string) => void;
}

export const ScenarioComparison: React.FC<ScenarioComparisonProps> = ({
  scenarios,
  onLoad,
  onDelete,
}) => {
  if (scenarios.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-card p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">Saved Scenarios</h2>
        <p className="text-gray-600">No saved scenarios yet. Create and save scenarios to compare them later.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-card p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Saved Scenarios</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usage Adj.</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cost Priority</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {scenarios.map((scenario) => (
              <tr key={scenario.id}>
                <td className="px-4 py-3 text-sm font-medium text-gray-900">{scenario.name}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{scenario.params.usageAdjustment}%</td>
                <td className="px-4 py-3 text-sm text-gray-600">{scenario.params.costPriority}%</td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {new Date(scenario.createdAt).toLocaleDateString()}
                </td>
                <td className="px-4 py-3 text-sm text-right space-x-2">
                  <Button size="sm" variant="outline" onClick={() => onLoad(scenario.id)}>Load</Button>
                  <button onClick={() => onDelete(scenario.id)} className="text-red-600 hover:text-red-700">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

ScenarioComparison.displayName = 'ScenarioComparison';
