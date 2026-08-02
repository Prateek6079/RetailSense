"use client";
import { useRef, useState, useEffect } from "react";

export default function VerticalBarChart({
    data = [
    { label: "Good", value: 100, pattern: "diagonal" },
    { label: "Bad", value: 61, pattern: "diagonal" },
    { label: "Ugly", value: 38, pattern: "diagonal" },
        ],
    }) 
    {
    const max = 100;

    const chartRef = useRef(null);
    const [chartHeight, setChartHeight] = useState(0);

    useEffect(() => {
        if (chartRef.current) {
        setChartHeight(chartRef.current.clientHeight);
        }
    }, []);

    return (
    <div ref={chartRef} className="flex w-full items-end justify-between gap-4 p-2 bg-black h-full">
        <svg width="0" height="0">
        <defs>
            <pattern
            id="diagonal"
            width="8"
            height="8"
            patternUnits="userSpaceOnUse"
            patternTransform="rotate(45)"
            >
            <line
                x1="0"
                y1="0"
                x2="0"
                y2="8"
                stroke="white"
                strokeWidth="2"
            />
            </pattern>
        </defs>
        </svg>

        <div className="flex w-full h-full items-end">

        {data.map((item) => {
        const usableHeight = chartHeight - 60; // reserve space for labels/percentages
        const height = (item.value / max) * usableHeight;

        return (
            <div
            key={item.label}
            className="flex-1 text-center"
            >
            <div className="text-sm mb-2">{item.value}%</div>

            <svg
                width="100%"
                height={height}
                viewBox={`0 0 40 ${height}`}
                className="overflow-visible"
            >
                <rect
                x="0"
                y="0"
                width="40"
                height={height}
                fill={`url(#${item.pattern})`}
                stroke="white"
                strokeWidth="2"
                />
            </svg>

            <div className="mt-3 text-sm leading-tight break-words">
                {item.label}
            </div>
            </div>
        );
        })}
        </div>
    </div>
    );
}