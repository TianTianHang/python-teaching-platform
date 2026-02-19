
import { redirect } from "react-router";
import { DEFAULT_META } from "~/config/meta";

export function loader(){
  return redirect("/auth/login")
}
export default function Home() {

  return <>
    <title>{DEFAULT_META.siteName}</title>
    <meta name="description" content={DEFAULT_META.description} />
    <meta property="og:title" content={DEFAULT_META.siteName} />
    <meta property="og:description" content={DEFAULT_META.description} />
    <meta property="og:type" content={DEFAULT_META.ogType} />
    <div>
      Welcome to my index
    </div>
  </>;
}
