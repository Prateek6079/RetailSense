"use client";

import { Eye, EyeOff } from "lucide-react";

const achievements = [
  {
    id: "list-1",
    name: "Season : Good",
    description: "Tracks Seasonal Trends",
    achievedAt: "2024-01-01T00:00:00Z",
  },
  {
    id: "list-2",
    name: "Pricing : Okay",
    description: "Tracks Pricing Trends",
    achievedAt: "2024-01-01T00:00:00Z",
  },
  {
    id: "list-3",
    name: "Sales : Good",
    description: "Tracks Sales Trends",
    achievedAt: null,
  },
  {
    id: "list-4",
    name: "Product Popularity : Good",
    description: "Tracks Product Popularity Trends",
    achievedAt: null,
  },
  {
    id: "list-5",
    name: "Operations : Smooth",
    description: "Tracks Operations Trends",
    achievedAt: null,
  },
];

export default function AchievementList() {
  return (
    <div className="flex flex-col gap-1 pl-2 pr-2 pb-2 h-full">
      {achievements.map((achievement) => {
        const unlocked = achievement.achievedAt !== null;

        return (
          <div
            key={achievement.id}
            className="flex min-h-0 items-center gap-2 border px-4 py-3"
          >
            <div
              className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl ${
                unlocked
                  ? "bg-gray-200 text-gray-700"
                  : "bg-gray-800 text-white"
              }`}
            >
              {unlocked ? <Eye className="h-6 w-6" /> : <EyeOff className="h-6 w-6" />}
            </div>

            <div className="min-w-0 flex-1">
              <h3
                className={`truncate text-base font-medium ${
                  !unlocked ? "text-gray-500" : ""
                }`}
              >
                {achievement.name}
              </h3>

              <p className="truncate text-xs text-gray-500">
                {achievement.description}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}