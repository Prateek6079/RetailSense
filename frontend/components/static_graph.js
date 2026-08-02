"use client";
import { ReactFlow } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { nodeStyle, edgeStyle } from "./graph_styling";
import CustomNode from "./customNode";
import FlowEdge from "./flowEdge";

const nodeTypes = {
  custom : CustomNode,
};

const edgeTypes = {
  animated: FlowEdge,
};


const nodes = [
    {
      id: "Profit",
      type: "custom",
      position: { x: 300, y: 0 },
      data: { 
        title: "Profit",
        type: "Intermediate",
        labels: [
          { name: "Increase", probability: 64 },
          { name: "Stable", probability: 25 },
          { name: "Decrease", probability: 11 },
        ],
       },
      style: nodeStyle,
    },
    {
      id: "Sales",
      type: "custom",
      position: { x: -200, y: 250 },
      data: { title: "Sales",
              type: "Intermediate",
              labels: [
              { name: "Increase", probability: 64 },
              { name: "Stable", probability: 25 },
              { name: "Decrease", probability: 11 },
              ],
            },
      style: nodeStyle,
    },
    {
      id: "Pricing",
      type: "custom",
      position: { x: 600, y: 400 },
      data: { 
        title: "Pricing",
        type: "Intermediate",
        labels: [
          { name: "Increase", probability: 64 },
          { name: "Stable", probability: 25 },
          { name: "Decrease", probability: 11 },
        ],
       },
      style: nodeStyle,
    },
    {
      id: "Costs",
      type: "custom",
      position: { x: 1000, y: 500 },
      data: { 
        title: "Costs",
        type: "Intermediate",
        labels: [
          { name: "Increase", probability: 64 },
          { name: "Stable", probability: 25 },
          { name: "Decrease", probability: 11 },
        ],
       },
      style: nodeStyle,
    },
    {
      id: "Strategic Levers",
      type: "custom",
      position: { x: 200, y: 300 },
      data: { 
        title: "Strategic Levers",
        type: "Intermediate",
        labels: [
          { name: "Increase", probability: 64 },
          { name: "Stable", probability: 25 },
          { name: "Decrease", probability: 11 },
        ],
       },
      style: nodeStyle,
    },
    {
      id: "Stocking",
      type: "custom",
      position: { x: 750, y: 900 },
      data: {
        title: "Stocking",
        type: "Intermediate",
        labels: [
          { name: "Increase", probability: 64 },
          { name: "Stable", probability: 25 },
          { name: "Decrease", probability: 11 },
        ],
      },
      style: nodeStyle,
    },
    {
      id: "Operational Efficiency",
      type: "custom",
      position: { x: 1250, y: 1250 },
      data: { 
        title: "Operational Efficiency",
        type: "Intermediate",
        labels: [
          { name: "Increase", probability: 64 },
          { name: "Stable", probability: 25 },
          { name: "Decrease", probability: 11 },
        ],
       },
      style: nodeStyle,
    },
    {
      id: "External Factors",
      type: "custom",
      position: { x: -500, y: 600 },
      data: { 
        title: "External Factors",
        type: "Intermediate",
        labels: [
          { name: "Increase", probability: 64 },
          { name: "Stable", probability: 25 },
          { name: "Decrease", probability: 11 },
        ],
       },
      style: nodeStyle,
    },
    {
      id: "Competition",
      type: "custom",
      position: { x: -300, y: 1250 },
      data: {
        title: "Competition",
        type: "Intermediate",
        labels: [
          { name: "Increase", probability: 64 },
          { name: "Stable", probability: 25 },
          { name: "Decrease", probability: 11 },
        ],
      },
      style: nodeStyle,
    },
    {
      id: "Economy",
      type: "custom",
      position: { x: 50, y: 1250 },
      data: {
        title: "Economy",
        type: "Intermediate",
        labels: [
          { name: "Increase", probability: 64 },
          { name: "Stable", probability: 25 },
          { name: "Decrease", probability: 11 },
        ],
      },
      style: nodeStyle,
    },
    {
      id: "Season",
      type: "custom",
      position: { x: -700, y: 1250 },
      data: { 
        title: "Season",
        type: "Intermediate",
        labels: [
          { name: "Increase", probability: 64 },
          { name: "Stable", probability: 25 },
          { name: "Decrease", probability: 11 },
        ],
       },
      style: nodeStyle,
    },
    {
      id: "Product Popularity",
      type: "custom",
      position: { x: 500, y: 1250 },
      data: { 
        title: "Product Popularity",
        type: "Intermediate",
        labels: [
          { name: "Increase", probability: 64 },
          { name: "Stable", probability: 25 },
          { name: "Decrease", probability: 11 },
        ],
       },
      style: nodeStyle,
    },
  ];

const edges = [
    {
      id: "1",
      type: "animated",
      source: "Profit",
      sourceHandle: "left",
      target: "Sales",
      targetHandle: "top",
      data: { speed: 100 },
    },
    {
      id: "2",
      type: "animated",
      source: "Profit",
      sourceHandle: "bottom",
      target: "Pricing",
      data: { speed: 100 },
    },
    {
      id: "3",
      type: "animated",
      source: "Profit",
      sourceHandle: "right",
      target: "Costs",
      targetHandle: "top",
      data: { speed: 100 },
    },
    {
      id: "4",
      type: "animated",
      source: "Sales",
      sourceHandle: "right",
      target: "Strategic Levers",
      targetHandle: "left",
      data: { speed: 100 },
    },
    {
      id: "5",
      type: "animated",
      source: "Sales",
      sourceHandle: "left",
      target: "External Factors",
      targetHandle: "top",
      data: { speed: 100 },
    },
    {
      id: "6",
      type: "animated",
      source: "Sales",
      sourceHandle: "bottom",
      target: "Product Popularity",
      targetHandle: "top",
      data: { speed: 100 },
    },
    {
      id: "7",
      type: "animated",
      source: "Strategic Levers",
      sourceHandle: "right",
      target: "Pricing",
      targetHandle: "left",
      data: { speed: 100 },
    },
    {
      id: "8",
      type: "animated",
      source: "Strategic Levers",
      sourceHandle: "bottom",
      target: "Stocking",
      targetHandle: "top",
      data: { speed: 100 },
    },
    {
      id: "9",
      type: "animated",
      source: "Pricing",
      sourceHandle: "right",
      target: "Costs",
      targetHandle: "left",
      data: { speed: 100 },
    },
    {
      id: "10",
      type: "animated",
      source: "Costs",
      sourceHandle: "bottom",
      target: "Operational Efficiency",
      data: { speed: 100 },
    },
    {
      id: "11",
      type: "animated",
      source: "Costs",
      sourceHandle: "bottom",
      target: "Stocking",
      data: { speed: 100 },
    },
    {
      id: "12",
      type: "animated",
      source: "Stocking",
      sourceHandle: "bottom",
      target: "Product Popularity",
      targetHandle: "right",
      data: { speed: 100 },
    },
    {
      id: "13",
      type: "animated",
      source: "External Factors",
      sourceHandle: "bottom",
      target: "Season",
      data: { speed: 100 },
    },
    {
      id: "14",
      type: "animated",
      source: "External Factors",
      sourceHandle: "right",
      target: "Economy",
      data: { speed: 100 },
    },
    {
      id: "15",
      type: "animated",
      source: "External Factors",
      sourceHandle: "bottom",
      target: "Competition",
      data: { speed: 100 }, // slower speed for this edge
    },
  ];

export default function StaticGraph() {
  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      defaultEdgeOptions={{
        type: "straight",
        style: edgeStyle,
      }}
      nodeTypes={nodeTypes}
      edgeTypes={edgeTypes}
      defaultViewport={{
        x: 400,
        y: 60,
        zoom: 0.5,
      }}
      zoomOnScroll={false}
      zoomOnPinch={false}
      zoomOnDoubleClick={false}
      panOnDrag={false}
      panOnScroll={false}
      nodesDraggable={false}
      nodesConnectable={false}
      elementsSelectable={false}
      preventScrolling={false}
      proOptions={{ hideAttribution: true }}
    />
  );
}