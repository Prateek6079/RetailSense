"use client";

import PieChart from "./pieChart";

const GRAPH_PATTERNS = ["result-diagonal", "result-dots", "result-cross"];
const PIE_PATTERNS = [
  "CustomDiagonal",
  "vertical",
  "h_points",
  "horizontal",
  "grid",
  "dots",
];
const PIE_VARIABLES = [
  ["Levers", "Strategic Levers"],
  ["Stocking", "Stocking"],
  ["Competition", "Competition"],
  ["Economy", "Economy"],
  ["Popularity", "Product Popularity"],
  ["Operations", "Operational Efficiency"],
];

function ResultGraph({ variables }) {
  const entries = Object.entries(variables);
  const rowHeight = 78;
  const graphHeight = 58 + entries.length * rowHeight;
  const graphWidth = 900;
  const variableLeft = 0;
  const labelLeft = 170;
  const plotLeft = 300;
  const plotWidth = 500;
  const barHeight = 12;

  return (
    <div className="overflow-x-auto border-t border-white/15 pt-4">
      <svg
        role="img"
        aria-label="Grouped probability chart for every simulation variable"
        viewBox={`0 0 ${graphWidth} ${graphHeight}`}
        className="h-auto min-w-[680px] w-full"
      >
        <defs>
          <pattern id="result-diagonal" width="8" height="8" patternUnits="userSpaceOnUse">
            <path d="M-2 2L2-2M0 8L8 0M6 10L10 6" stroke="white" strokeWidth="1" />
          </pattern>
          <pattern id="result-dots" width="7" height="7" patternUnits="userSpaceOnUse">
            <circle cx="3.5" cy="3.5" r="1.5" fill="white" />
          </pattern>
          <pattern id="result-cross" width="8" height="8" patternUnits="userSpaceOnUse">
            <path d="M0 4H8M4 0V8" stroke="white" strokeWidth="1" />
          </pattern>
        </defs>

        {[0, 25, 50, 75, 100].map((tick) => {
          const x = plotLeft + (tick / 100) * plotWidth;
          return (
            <g key={tick}>
              <line x1={x} y1="38" x2={x} y2={graphHeight - 8} stroke="white" strokeOpacity="0.12" />
              <text x={x} y="20" fill="#a3a3a3" fontSize="11" textAnchor="middle">
                {tick}%
              </text>
            </g>
          );
        })}

        {entries.map(([variable, probabilities], rowIndex) => {
          const y = 40 + rowIndex * rowHeight;
          const labels = Object.entries(probabilities).filter(
            ([label]) => label !== "Speculate",
          );
          return (
            <g key={variable}>
              <text x={variableLeft} y={y + 25} fill="#ededed" fontSize="12" fontWeight="600">
                {variable}
              </text>
              {labels.map(([label, probability], labelIndex) => {
                const barY = y + labelIndex * 19;
                const width = Math.max(2, probability * plotWidth);
                return (
                  <g key={label}>
                    <text x={labelLeft} y={barY + 10} fill="#a3a3a3" fontSize="10">
                      {label}
                    </text>
                    <rect
                      x={plotLeft}
                      y={barY}
                      width={width}
                      height={barHeight}
                      fill={`url(#${GRAPH_PATTERNS[labelIndex % GRAPH_PATTERNS.length]})`}
                      stroke="white"
                      strokeOpacity="0.8"
                    />
                    <text x={plotLeft + width + 8} y={barY + 10} fill="#ededed" fontSize="10">
                      {Math.round(probability * 100)}%
                    </text>
                  </g>
                );
              })}
              <line x1={variableLeft} y1={y + rowHeight - 7} x2={graphWidth} y2={y + rowHeight - 7} stroke="white" strokeOpacity="0.12" />
            </g>
          );
        })}
        <text x={plotLeft + plotWidth / 2} y={graphHeight - 1} fill="#a3a3a3" fontSize="10" textAnchor="middle">
          Probability
        </text>
      </svg>
    </div>
  );
}

export default function SimulationResults({ result }) {
  if (!result) return null;

  const variables = result.variables || {};
  const configuration = result.configuration || {};
  const configuredProbabilities = Object.entries(variables).map(([variable, probabilities]) => ({
    label: variable,
    value: Math.round((probabilities[configuration[variable]] || 0) * 100),
    pattern: GRAPH_PATTERNS[Object.keys(variables).indexOf(variable) % GRAPH_PATTERNS.length],
  }));
  const pieData = PIE_VARIABLES.flatMap(([label, variable]) => {
    const probabilities = variables[variable];
    if (!probabilities) return [];

    return [{
      label,
      value: Math.round((probabilities[configuration[variable]] || 0) * 100),
      pattern: PIE_PATTERNS[PIE_VARIABLES.findIndex(([, name]) => name === variable)],
    }];
  });
  const calculatedScore = configuredProbabilities.length
    ? Math.round(configuredProbabilities.reduce((sum, item) => sum + item.value, 0) / configuredProbabilities.length)
    : 0;
  const probability = result.score ?? calculatedScore / 100;

  return (
    <section aria-label="Simulation results" className="mt-5 border-t border-white/15 pt-4">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h3 className="text-sm font-semibold text-foreground">Simulation result</h3>
          <span className="text-xs text-muted-foreground">Completed</span>
        </div>
        <div className="text-right">
          <span className="block text-[10px] uppercase tracking-[0.18em] text-muted-foreground">Probability</span>
          <strong className="text-3xl leading-none text-foreground">{Math.round(probability * 100)}%</strong>
        </div>
      </div>

      <div className="grid items-stretch gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(280px,0.85fr)]">
        <div className="h-full border border-white/15 bg-black/20 p-3">
          <h4 className="mb-3 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">Configuration</h4>
          <dl className="grid gap-x-8 gap-y-2 sm:grid-cols-2">
            {Object.entries(configuration).map(([variable, value]) => (
              <div key={variable} className="flex items-center justify-between gap-3 border-b border-white/10 pb-2 text-xs">
                <dt className="text-[10px] font-semibold uppercase tracking-[0.08em] text-muted-foreground">
                  {variable}
                </dt>
                <dd className="shrink-0 border border-white/70 bg-white px-2 py-1 font-semibold text-black">
                  {value}
                </dd>
              </div>
            ))}
          </dl>
        </div>
        <div className="h-full min-h-[220px] border border-white/15 bg-black/20 p-2 lg:max-h-[280px]">
          <div className="h-full w-full">
            <PieChart data={pieData} />
          </div>
        </div>
      </div>

      <ResultGraph variables={variables} />
    </section>
  );
}
