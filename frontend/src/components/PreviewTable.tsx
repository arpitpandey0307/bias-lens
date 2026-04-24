interface PreviewTableProps {
  data: Record<string, any>[];
  rowCount: number;
  columnCount: number;
}

export default function PreviewTable({ data, rowCount, columnCount }: PreviewTableProps) {
  if (data.length === 0) return null;

  const columns = Object.keys(data[0]);

  return (
    <div className="mt-6">
      <div className="mb-4">
        <h3 className="text-headline-sm font-medium text-on-surface">Data Preview</h3>
        <p className="text-body-md text-on-surface-variant mt-1">
          Showing first {data.length} of {rowCount} rows · {columnCount} columns
        </p>
      </div>

      <div className="overflow-x-auto bg-surface-container-lowest rounded-lg shadow-ambient">
        <table className="w-full">
          <thead>
            <tr className="bg-surface-container-low">
              {columns.map((col) => (
                <th
                  key={col}
                  className="px-4 py-3 text-left text-label-sm uppercase tracking-wider text-on-surface-variant font-medium"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr
                key={idx}
                className={idx % 2 === 0 ? 'bg-surface' : 'bg-surface-container-low'}
              >
                {columns.map((col) => (
                  <td key={col} className="px-4 py-3 text-body-md text-on-surface">
                    {row[col] !== null && row[col] !== undefined ? String(row[col]) : '—'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
