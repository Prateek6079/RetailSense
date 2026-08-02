"use client";

import { BaseEdge, getStraightPath } from "@xyflow/react";

export default function AnimatedSVGEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  data,
}) {
  const [edgePath] = getStraightPath({
    targetX,
    targetY,
    sourceX,
    sourceY,
  });

  const length = Math.hypot(targetX - sourceX, targetY - sourceY);

  const speed = data?.speed ?? 150; // default if not provided

  const duration = length / speed;

  return (
    <>
      <BaseEdge id={id} path={edgePath} />

      <path d="M -12 -8 L 12 0 L -12 8 Z" fill="white">
        <animateMotion
          dur={`${duration}s`}
          repeatCount="indefinite"
          path={edgePath}
          keyPoints="1;0" // 0:1 when direction is reversed
          keyTimes="0;1"
          rotate="auto-reverse" // auto when direction is reversed
        />
      </path>
    </>
  );
}