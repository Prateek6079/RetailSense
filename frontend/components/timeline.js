const milestones = [
  {
    day: 1,
    title: "Planning",
    description: "Scope definition",
    completed: true,
  },
  {
    day: 2,
    title: "Design",
    description: "UI/UX design and prototyping.",
    completed: true,
  },
  {
    day: 3,
    title: "Development",
    description: "Core features implementation.",
    completed: true,
  },
  {
    day: 4,
    title: "Deployment",
    description: "Core features implementation.",
    completed: false,
  },
  {
    day: 5,
    title: "feedback",
    description: "Core features implementation.",
    completed: false,
  },
];

export default function RewardTimeline() {
  return (
    <div className="flex w-full">
      {milestones.map((item, index) => (
        <div key={index} className={`relative flex-1`}>
          {/* Connecting line */}
          {index !== milestones.length - 1 && (
            <div className={`absolute left-6 right-0 top-3 h-px bg-zinc-700
              ${milestones[index+1].completed ? "border-2" : ""}`} />
          )}

          {/* Circle */}
          <div
            className={`relative z-10 h-6 w-6 rounded-full border-2 ${
              item.completed
                ? "border-white bg-zinc-900"
                : "border-zinc-700 bg-zinc-950"
            }`}
          />

          {/* Text */}
          <div className="mt-6">
            <p className="text-sm text-zinc-400">Day {item.day}</p>

            <h3 className="font-semibold">{item.title}</h3>

            <p className="mt-1 text-sm text-zinc-500">
              {item.description}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}