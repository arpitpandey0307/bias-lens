import type { GroupStatistics } from '../types';

interface ConfusionMatrixHeatmapProps {
  groupStatistics: Record<string, GroupStatistics>;
}

export default function ConfusionMatrixHeatmap({ groupStatistics }: ConfusionMatrixHeatmapProps) {
  return (
    <div className="bg-surface-container-lowest rounded-lg shadow-ambient p-6">
      <h3 className="text-headline-sm font-medium text-on-surface mb-4">
        Confusion Matrices
      </h3>
      <p className="text-body-md text-on-surface-variant mb-6">
        Prediction accuracy breakdown for each group
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {Object.entries(groupStatistics).map(([group, stats]) => {
          const { confusion_matrix } = stats;
          const total =
            confusion_matrix.true_positive +
            confusion_matrix.false_positive +
            confusion_matrix.true_negative +
            confusion_matrix.false_negative;

          const getIntensity = (value: number) => {
            const percentage = (value / total) * 100;
            if (percentage > 40) return 'bg-primary text-on-primary';
            if (percentage > 20) return 'bg-primary-container text-on-primary-container';
            if (percentage > 10) return 'bg-surface-container-high text-on-surface';
            return 'bg-surface-container-low text-on-surface-variant';
          };

          return (
            <div key={group} className="border border-outline-variant rounded-lg p-4">
              <h4 className="text-body-md font-medium text-on-surface mb-3">{group}</h4>
              
              <div className="grid grid-cols-2 gap-2">
                {/* True Positive */}
                <div className={`p-4 rounded ${getIntensity(confusion_matrix.true_positive)} text-center`}>
                  <div className="text-label-sm uppercase tracking-wider mb-1">True Positive</div>
                  <div className="text-xl font-medium">{confusion_matrix.true_positive}</div>
                  <div className="text-label-sm mt-1">
                    {((confusion_matrix.true_positive / total) * 100).toFixed(1)}%
                  </div>
                </div>

                {/* False Positive */}
                <div className={`p-4 rounded ${getIntensity(confusion_matrix.false_positive)} text-center`}>
                  <div className="text-label-sm uppercase tracking-wider mb-1">False Positive</div>
                  <div className="text-xl font-medium">{confusion_matrix.false_positive}</div>
                  <div className="text-label-sm mt-1">
                    {((confusion_matrix.false_positive / total) * 100).toFixed(1)}%
                  </div>
                </div>

                {/* False Negative */}
                <div className={`p-4 rounded ${getIntensity(confusion_matrix.false_negative)} text-center`}>
                  <div className="text-label-sm uppercase tracking-wider mb-1">False Negative</div>
                  <div className="text-xl font-medium">{confusion_matrix.false_negative}</div>
                  <div className="text-label-sm mt-1">
                    {((confusion_matrix.false_negative / total) * 100).toFixed(1)}%
                  </div>
                </div>

                {/* True Negative */}
                <div className={`p-4 rounded ${getIntensity(confusion_matrix.true_negative)} text-center`}>
                  <div className="text-label-sm uppercase tracking-wider mb-1">True Negative</div>
                  <div className="text-xl font-medium">{confusion_matrix.true_negative}</div>
                  <div className="text-label-sm mt-1">
                    {((confusion_matrix.true_negative / total) * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
