import JupyterLiteEmbed from "~/components/JupyterLiteEmbed";

import { useLocation } from "react-router";
import type { Route } from "./+types/jupyterlite.$";



export default function JupyterLite({ params }: Route.ComponentProps) {
    const  location = useLocation()
    return (
        <JupyterLiteEmbed url={location.pathname}/>
    );
}