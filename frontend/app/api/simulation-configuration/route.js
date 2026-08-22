import { readFile } from "fs/promises";
import path from "path";

export const dynamic = "force-dynamic";

const configurationPath = path.join(
  process.cwd(),
  "data",
  "simulation-configuration.json",
);

export async function GET() {
  const file = await readFile(configurationPath, "utf8");
  return Response.json(JSON.parse(file));
}
