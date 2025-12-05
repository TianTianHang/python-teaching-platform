import JupyterLiteEmbed from "~/components/JupyterLiteEmbed";

import { useLocation } from "react-router";



export default function JupyterLite() {
    const  location = useLocation()
    return (
        <JupyterLiteEmbed url={location.pathname}/>
    );
}