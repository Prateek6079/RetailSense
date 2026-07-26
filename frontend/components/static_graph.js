"use client";
import { Background, ReactFlow } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { nodeStyle, edgeStyle } from "./graph_styling";
import CustomNode from "./customNode";

const nodeTypes = {
  custom : CustomNode,
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
      source: "Profit",
      sourceHandle: "left",
      target: "Sales",
      targetHandle: "top",
    },
    {
      id: "2",
      source: "Profit",
      sourceHandle: "bottom",
      target: "Pricing",
    },
    {
      id: "3",
      source: "Profit",
      sourceHandle: "right",
      target: "Costs",
      targetHandle: "top",
    },
    {
      id: "4",
      source: "Sales",
      sourceHandle: "right",
      target: "Strategic Levers",
      targetHandle: "left",
    },
    {
      id: "5",
      source: "Sales",
      sourceHandle: "left",
      target: "External Factors",
      targetHandle: "top",
    },
    {
      id: "6",
      source: "Sales",
      sourceHandle: "bottom",
      target: "Product Popularity",
      targetHandle: "top",
    },
    {
      id: "7",
      source: "Strategic Levers",
      sourceHandle: "right",
      target: "Pricing",
      targetHandle: "left",
    },
    {
      id: "8",
      source: "Strategic Levers",
      sourceHandle: "bottom",
      target: "Stocking",
      targetHandle: "top",
    },
    {
      id: "9",
      source: "Pricing",
      sourceHandle: "right",
      target: "Costs",
      targetHandle: "left",
    },
    {
      id: "10",
      source: "Costs",
      sourceHandle: "bottom",
      target: "Operational Efficiency",
    },
    {
      id: "11",
      source: "Costs",
      sourceHandle: "bottom",
      target: "Stocking",
    },
    {
      id: "12",
      source: "Stocking",
      sourceHandle: "bottom",
      target: "Product Popularity",
      targetHandle: "right",
    },
    {
      id: "13",
      source: "External Factors",
      sourceHandle: "bottom",
      target: "Season",
    },
    {
      id: "14",
      source: "External Factors",
      sourceHandle: "right",
      target: "Economy",
    },
    {
      id: "15",
      source: "External Factors",
      sourceHandle: "bottom",
      target: "Competition",
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
      proOptions={{ hideAttribution: true }}
    />
  );
}