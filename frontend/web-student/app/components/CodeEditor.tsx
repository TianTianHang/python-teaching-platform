import CodeMirror, { ViewUpdate } from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python'
import { useCallback, useState } from 'react';



export default function CodeEditor() {
    const [codeValue, setCodeValue] = useState<string>("print('hello world!')")
    const onChange = useCallback((val:string, viewUpdate:ViewUpdate) => {
        setCodeValue(val);
    }, []);
    return <>
        <CodeMirror value={codeValue} height="200px" extensions={[python()]} onChange={onChange} />
    </>
}