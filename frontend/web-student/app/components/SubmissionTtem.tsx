import { Box, Card, Grid, Typography } from "@mui/material";
import type { Submission } from "~/types/submission";

export default function SubmissionItem({ submission}: {submission:Submission,reUseCode?:(code:string)=>void}) {
     // 获取状态颜色
    const getStatusColor = (status: string) => {
        switch(status) {
            case 'accepted': return '#4caf50';
            case 'wrong_answer': return '#f44336';
            case 'time_limit_exceeded': return '#ff9800';
            case 'memory_limit_exceeded': return '#ff9800';
            case 'runtime_error': return '#f44336';
            case 'compilation_error': return '#f44336';
            case 'pending': return '#9e9e9e';
            case 'judging': return '#2196f3';
            default: return '#9e9e9e';
        }
    };
    return (
        <Card key={submission.id} variant="outlined" sx={{ p: 2 }}>
            <Grid container justifyContent="space-between" alignItems="center">
                <Grid >
                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                        提交 #{submission.id}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        状态: <span style={{ color: getStatusColor(submission.status) }}>{submission.status}</span> |
                        时间: {submission.execution_time ? `${submission.execution_time}ms` : 'N/A'} |
                        内存: {submission.memory_used ? `${submission.memory_used}KB` : 'N/A'}
                    </Typography>
                </Grid>
                <Grid>
                    {/* <Button size="small" onClick={() => reUseCode?.(submission.code)}>
                        重新使用
                    </Button> */}
                </Grid>
            </Grid>
            {submission.output && (
                <Box sx={{ mt: 1 }}>
                    <Typography variant="body2" sx={{ wordBreak: 'break-word', whiteSpace: 'pre-wrap' }}>
                        输出: {submission.output}
                    </Typography>
                </Box>
            )}
            {submission.error && (
                <Box sx={{ mt: 1 }}>
                    <Typography variant="body2" color="error" sx={{ wordBreak: 'break-word', whiteSpace: 'pre-wrap' }}>
                        错误: {submission.error}
                    </Typography>
                </Box>
            )}
        </Card>
    )

}