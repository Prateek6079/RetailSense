import { readFile, writeFile } from "fs/promises";
import path from "path";

export const dynamic = "force-dynamic";

const simulationsPath = path.join(process.cwd(), "data", "simulations.json");

async function getSimulations() {
  const file = await readFile(simulationsPath, "utf8");
  return JSON.parse(file);
}

export async function GET() {
  return Response.json(await getSimulations());
}

export async function POST(request) {
  const { name } = await request.json();
  const simulation = {
    id: crypto.randomUUID(),
    title: name || "Untitled Simulation",
    description: "A new simulation ready for configuration.",
    configuration: null,
  };
  const simulations = await getSimulations();
  simulations.push(simulation);
  await writeFile(simulationsPath, `${JSON.stringify(simulations, null, 2)}\n`);

  return Response.json(simulation, { status: 201 });
}

export async function DELETE(request) {
  const id = new URL(request.url).searchParams.get("id");
  const simulations = await getSimulations();
  const remainingSimulations = simulations.filter((simulation) => simulation.id !== id);

  if (remainingSimulations.length === simulations.length) {
    return Response.json({ error: "Simulation not found" }, { status: 404 });
  }

  await writeFile(
    simulationsPath,
    `${JSON.stringify(remainingSimulations, null, 2)}\n`,
  );

  return new Response(null, { status: 204 });
}

export async function PATCH(request) {
  const { id, name, configuration, result, score } = await request.json();
  const simulations = await getSimulations();
  const simulation = simulations.find((item) => item.id === id);

  if (!simulation) {
    return Response.json({ error: "Simulation not found" }, { status: 404 });
  }

  if (typeof name === "string" && name.trim()) {
    simulation.title = name.trim();
  }
  simulation.configuration = configuration;
  if (result !== undefined) simulation.result = result;
  if (score !== undefined) simulation.score = score;
  await writeFile(simulationsPath, `${JSON.stringify(simulations, null, 2)}\n`);

  return Response.json(simulation);
}
