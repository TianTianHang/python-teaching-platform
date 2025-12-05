import { Typography, Divider } from "@mui/material";
import MarkdownRenderer from "~/components/MarkdownRenderer";
import { useRouteLoaderData } from "react-router";

export default function ProblemDescription() {
    const data = useRouteLoaderData("routes/problems.$problemId");
    const problem = data.problem;
    return (
        <>
            <Typography variant="h4">{`${problem.id}. ${problem.title}`}</Typography>
            <Divider sx={{ my: 2 }} />
            <Typography variant="h5" gutterBottom>题目描述</Typography>
            <MarkdownRenderer markdownContent={problem.content} />
        </>
    );
}