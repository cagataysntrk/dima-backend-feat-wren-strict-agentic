import type { Metadata } from "next";
import { BrowseData } from "./BrowseData";

export const metadata: Metadata = { title: "Veriler" };

export default function DataPage() {
  return <BrowseData />;
}
