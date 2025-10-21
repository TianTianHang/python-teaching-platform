// LanguageEditor.tsx
import {
    Box,
    Button,
    ButtonGroup,
    CircularProgress,
    FormControl,
    Grid,
    InputLabel,
    MenuItem,
    Select,
    Stack,
    Typography, // Added Typography
} from '@mui/material';
import React, { useState, Suspense, lazy } from 'react';
import { useSubmission } from '~/hooks/useSubmission';
import SubmissionResult from './SubmissionResult';

const MonacoEditor = lazy(() => import('@monaco-editor/react'));

// Supported languages (Monaco built-in)
const LANGUAGES = [
    { label: 'JavaScript', value: 'javascript', id:63},
    { label: 'TypeScript', value: 'typescript',id:74 },  
    { label: 'Python3', value: 'python3', id: 71 },
    { label: 'Java', value: 'java',id:62 },
];

interface CodeEditorProps {
    language?: string;
    onChange?: (value: string | undefined) => void;
    height?: string | number;
    theme?: 'vs' | 'vs-dark' | 'hc-black';
    options?: any;
}

export default function CodeEditor(props: CodeEditorProps){
    const [language, setLanguage] = useState<string>(props?.language || 'python3');
    const [code, setCode] = useState<string>('print("Hello, Judge0!")');
    const [isSubmit,setIsSubmit] = useState<boolean>(false);
    const { submitCode, isPolling, result, error } = useSubmission();
    const handleLanguageChange = (e: { target: { value: React.SetStateAction<string> } }) => {
        setLanguage(e.target.value);
    };
    const handelSubmit = async () => {
        // ✅ 根据当前 language 字符串查找对应的 language_id
        const selectedLang = LANGUAGES.find(lang => lang.value === language);
        if (!selectedLang) {
            console.error('Unknown language:', language);
            return;
        }

        setIsSubmit(true);
        try {
            await submitCode({
                source_code: code,
                language_id: selectedLang.id, // ✅ 动态 ID
            });
        } catch (err) {
            // 错误已在 useSubmission 中处理，这里可选加日志
        }
    };
    const onCodeChange = (value: string | undefined) => {
        setCode(value || '');
        props.onChange?.(value);
    };

    return (
        <Stack spacing={3} sx={{ p: 3, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}> {/* Added padding and border to the Stack */}
            <Grid container spacing={2} alignItems="center"> {/* Adjusted spacing and added alignItems */}
                <Grid  > {/* Responsive grid for buttons */}
                    <ButtonGroup variant="contained" aria-label="code editor actions"> {/* Added variant to ButtonGroup */}
                        <Button color="primary" onClick={handelSubmit}>提交</Button>
                        <Button color="secondary" onClick={() => setCode("")}>重置</Button>
                    </ButtonGroup>
                </Grid>
                <Grid   display="flex" justifyContent={{ xs: 'flex-start', sm: 'flex-end' }}> {/* Responsive grid for language selector */}
                    <FormControl variant="outlined" size="small" sx={{ minWidth: 120 }}> {/* Added size="small" for compact look */}
                        <InputLabel id="language-select-label">Language</InputLabel>
                        <Select
                            labelId="language-select-label"
                            id="language-select"
                            value={language}
                            onChange={handleLanguageChange}
                            label="Language"
                        >
                            {LANGUAGES.map((lang) => (
                                <MenuItem key={lang.id} value={lang.value}>
                                    {lang.label}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>
            </Grid>

            {/* Monaco Editor (lazy loaded) */}
            <Suspense fallback={ <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: props.height || "500px" }}>
                        <CircularProgress /> {/* 使用 CircularProgress */}
                    </Box>}> {/* Used Typography for loading text */}
                <MonacoEditor
                    height={props.height || "500px"}
                    language={language}
                    value={code}
                    onChange={onCodeChange}
                    theme={props.theme || 'vs'}
                    options={props.options || {
                        minimap: { enabled: false },
                        fontSize: 14,
                        automaticLayout: true,
                    }}
                />
            </Suspense>
            <Box>
                {isSubmit?<SubmissionResult result={result} isPolling={isPolling} error={error}/>:<></>}
            </Box>
        </Stack>
    );
};


