import JupyterLiteEmbed from "~/components/JupyterLiteEmbed";





export default function JupyterLite() {
    return (
        <JupyterLiteEmbed url={"/jupyterlite/lab/index.html"}/>
    );
}