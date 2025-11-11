import React from 'react';
import { FileDown } from 'lucide-react';
import Papa from 'papaparse';
import { Button } from '@/components/design-system';
import type { UsageData, UserProfile } from '@/types/recommendation';

export interface CsvExportUsageProps {
  usageData: UsageData[];
  profile: UserProfile;
  userId?: string;
}

export const CsvExportUsage: React.FC<CsvExportUsageProps> = ({
  usageData,
  profile,
  userId = 'user',
}) => {
  const handleExport = () => {
    const csvData = usageData.map((data) => {
      const date = new Date(data.month);
      const month = date.toLocaleDateString('en-US', { month: 'long' });
      const year = date.getFullYear();
      const monthNum = date.getMonth();

      let season = 'Winter';
      if (monthNum >= 3 && monthNum <= 5) season = 'Spring';
      else if (monthNum >= 6 && monthNum <= 8) season = 'Summer';
      else if (monthNum >= 9 && monthNum <= 11) season = 'Fall';

      // Estimate cost (rough calculation)
      const estimatedCost = (data.kwh * 12) / 100; // Assuming 12¢/kWh average

      return {
        Month: month,
        Year: year,
        'kWh': data.kwh,
        'Estimated Cost ($)': estimatedCost.toFixed(2),
        Season: season,
        'Profile Type': profile.profile_type,
      };
    });

    const csv = Papa.unparse(csvData);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute(
      'download',
      `treebeard-usage-${userId}-${new Date().toISOString().split('T')[0]}.csv`
    );
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Button variant="secondary" onClick={handleExport}>
      <FileDown className="w-4 h-4 mr-2" />
      Download Usage Data (CSV)
    </Button>
  );
};

CsvExportUsage.displayName = 'CsvExportUsage';
