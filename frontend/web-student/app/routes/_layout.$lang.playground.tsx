import { Container } from "@mui/material";
import type { Route } from "./+types/_layout.$lang.playground";
import CodeEditor from "~/components/CodeEditor";
import { useState } from "react";




export default function PlaygroundPage({ params }: Route.ComponentProps) {
    const [code,setCode]=useState<string|undefined>("")
    return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>

        <CodeEditor
            height="500px"
            language="python3"
            onChange={setCode}
            theme="vs-dark"
            options={{
                minimap: { enabled: false },
                fontSize: 14,
            }} />
    </Container>
    )
}