
import { redirect } from "react-router";

export function meta() {
  return [
    { title: "New React Router App" },
    { name: "description", content: "Welcome to React Router!" },
  ];
}
export function loader(){
  return redirect("/auth/login")
}
export default function Home() {
  
  return <div>
    Welcome to my index
  </div> ;
}
