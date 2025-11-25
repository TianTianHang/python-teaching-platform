import JupyterLiteEmbed from "~/components/JupyterLiteEmbed";
import type { Route } from "./+types/_layout.jupyter";




export default function JupyterLite({ params }: Route.ComponentProps) {
    return (
        <JupyterLiteEmbed/>
    );
}