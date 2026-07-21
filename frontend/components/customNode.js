// CustomNode.jsx
import { Handle, Position } from "@xyflow/react";


export default function CustomNode({ data }) {
  return (
    <div
      style={{
        background: "var(--background)",
        color: "#fff",
        border: "2px solid #fff",
        borderRadius: 10,
        width: 220,
        padding: 12,
        fontSize: 14,
      }}
    >
      {/* Title */}
      <div
        style={{
          fontWeight: 700,
          textAlign: "center",
          marginBottom: 8,
        }}
      >
        {data.title}
      </div>

      <hr
        style={{
          border: 0,
          borderTop: "1px solid #666",
          margin: "8px 0",
        }}
      />

      {/* Type */}
      <div>
        <strong>Type:</strong> {data.type}
      </div>

      <div style={{ marginTop: 10 }}>
        <strong>Labels</strong>

        {data.labels.map((label, index) => (
          <div
            key={index}
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginTop: 4,
            }}
          >
            <span>{label.name}</span>
            <span>{label.probability}%</span>
          </div>
        ))}
      </div>
        <Handle type="source" position={Position.Top} id="top" />
        <Handle type="source" position={Position.Left} id="left" />
        <Handle type="source" position={Position.Right} id="right" />
        <Handle type="source" position={Position.Bottom} id="bottom" />

        <Handle type="target" position={Position.Top} id="top" />
        <Handle type="target" position={Position.Left} id="left" />
        <Handle type="target" position={Position.Right} id="right" />
        <Handle type="target" position={Position.Bottom} id="bottom" />
    </div>
  );
}