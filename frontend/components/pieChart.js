"use client";

export default function PieChart({
  data = [
    { label: "Levers", value: 25, pattern: "CustomDiagonal" },
    { label: "Stocking", value: 20, pattern: "vertical" },
    { label: "Competition", value: 15, pattern: "h_points" },
    { label: "Economy", value: 12, pattern: "horizontal" },
    { label: "Popularity", value: 18, pattern: "grid" },
    { label: "Operations", value: 10, pattern: "dots" },
  ],
}) {
  const total = data.reduce((sum, item) => sum + item.value, 0);


  return (
    <div className="flex w-full h-full bg-black">

        {/* Pie Chart */}
        <div className="flex-[3] min-w-0 h-full">
        <svg viewBox="0 0 210 250" className="h-full w-full">
            <g transform="translate(-20, 0)">

            <defs>

            {/* Diagonal */}
            <pattern
                id="CustomDiagonal"
                width="8"
                height="8"
                patternUnits="userSpaceOnUse"
            >
                <line
                x1="0"
                y1="0"
                x2="8"
                y2="8"
                stroke="white"
                strokeWidth="1"
                />
            </pattern>

            {/* Dots */}
            <pattern
                id="dots"
                width="4"
                height="4"
                patternUnits="userSpaceOnUse"
            >
                <circle
                cx="2"
                cy="2"
                r="1"
                fill="white"
                />
            </pattern>

            {/* hollow Points */}
            <pattern
                id="h_points"
                width="8"
                height="8"
                patternUnits="userSpaceOnUse"
            >
                <circle
                cx="4"
                cy="4"
                r="4"
                stroke="white"
                strokeWidth="1"
                fill="none"
                />
            </pattern>

            {/* Cross */}
            <pattern
                id="cross"
                width="8"
                height="8"
                patternUnits="userSpaceOnUse"
            >
                <path
                d="M0 4H8 M4 0V8"
                stroke="white"
                strokeWidth="1"
                />
            </pattern>

            {/* Horizontal */}
            <pattern
                id="horizontal"
                width="4"
                height="4"
                patternUnits="userSpaceOnUse"
            >
                <line
                x1="0"
                y1="2"
                x2="4"
                y2="2"
                stroke="white"
                strokeWidth="1"
                />
            </pattern>

            {/* Grid */}
            <pattern
                id="grid"
                width="8"
                height="8"
                patternUnits="userSpaceOnUse"
            >
                <path
                d="M0 4H8 M4 0V8"
                stroke="white"
                strokeWidth="1"
                />
            </pattern>

            {/* Vertical */}
            <pattern
                id="vertical"
                width="4"
                height="4"
                patternUnits="userSpaceOnUse"
            >
                <line
                x1="2"
                y1="0"
                x2="2"
                y2="4"
                stroke="white"
                strokeWidth="1"
                />
            </pattern>

            </defs>

            {(() => {
            let cumulative = 0;
            const circumference = 2 * Math.PI * 80;

            return data.map((item, i) => {
                const segment = (item.value / total) * circumference;

                cumulative += segment;

                return (
                <circle
                    key={i}
                    cx="125"
                    cy="125"
                    r="80"
                    fill="none"
                    stroke={`url(#${item.pattern})`}
                    strokeWidth="40"
                    strokeDasharray={`${segment} ${circumference - segment}`}
                    strokeDashoffset={`${cumulative}`}
                />
                );
            });
            })()}

            </g>
        </svg>
        </div>

        {/* Legend */}

        <div className="h-full p-1 justify-center flex-[2] min-w-0 flex-col flex gap-5">

            {data.map((item) => (

            <div
                key={item.label}
                className="flex items-center gap-1"
            >

                <svg
                width="16"
                height="16"
                viewBox="0 0 16 16"
                >
                <rect
                    width="16"
                    height="16"
                    fill={`url(#${item.pattern})`}
                    stroke="white"
                    strokeWidth="2"
                />
                </svg>

                <span className="text-xs">
                {item.label}
                </span>

                <span className="ml-1 text-xs opacity-70">
                {item.value}%
                </span>

            </div>

            ))}

        </div>

        </div>
  );
}