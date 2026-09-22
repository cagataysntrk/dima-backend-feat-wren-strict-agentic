import type { Metadata } from "next";
import { SchemaView } from "./SchemaView";

export const metadata: Metadata = { title: "Şema" };

export default function SchemaPage() {
  return <SchemaView />;
}
