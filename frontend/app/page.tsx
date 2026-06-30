import { redirect } from "next/navigation";

export default function Home() {
  // Auth-aware routing arrives in M1; for now the app opens on the dashboard.
  redirect("/dashboard");
}
