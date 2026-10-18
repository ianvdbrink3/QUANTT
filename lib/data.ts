import { readFile } from "node:fs/promises";
import path from "node:path";
import type { LabData } from "./types";
export async function loadData(): Promise<LabData> {
  const [quality, analytics, experiments, index] = await Promise.all(
    ["quality", "analytics", "experiments", "index"].map(async (name) =>
      JSON.parse(
        await readFile(
          path.join(process.cwd(), "public/data", `${name}.json`),
          "utf8",
        ),
      ),
    ),
  );
  return { quality, analytics, experiments, index };
}
