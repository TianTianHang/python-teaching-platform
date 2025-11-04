
import { redirect } from "react-router";
import type { Route } from "./+types/_index";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "New React Router App" },
    { name: "description", content: "Welcome to React Router!" },
  ];
}
export function loader({}:Route.ActionArgs){
  return redirect("/auth/login")
}
export default function Home() {
  
  return <div>
    Welcome to my index
  </div> ;
}
