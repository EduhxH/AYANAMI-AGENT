import { redirect } from "next/navigation";

export default function PreferencesPage() {
  redirect("/dashboard?settings=1");
}
