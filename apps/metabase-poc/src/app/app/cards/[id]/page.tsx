import { CardView } from "./CardView";

export default async function CardPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <CardView id={Number(id)} />;
}
