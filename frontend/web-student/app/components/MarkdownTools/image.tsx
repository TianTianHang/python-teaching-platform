import { codeBlock, type ICommand } from "@uiw/react-markdown-editor";
import ImageIcon from '@mui/icons-material/Image';
import CodeIcon from '@mui/icons-material/Code';
import { EditorSelection } from "@uiw/react-codemirror";
import { showNotification } from "../Notification";
async function uploadFile(file:File) {
    const formData = new FormData();
    formData.append('thread', file);

    // 这里的 '/upload' 是你的服务器接收文件上传的接口地址
    const response = await fetch('/upload/thread', {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        throw new Error('网络响应异常');
    }

    const data = await response.json();
    // 假设服务器返回的数据结构包含图片的URL
    return data.url;
}
export const image2: ICommand = {
    icon: <ImageIcon fontSize="small" />,
    execute: ({ state, view }) => {
        if (!state || !view) return;
        const main = view.state.selection.main;
        const txt = view.state.sliceDoc(view.state.selection.main.from, view.state.selection.main.to);
        // 创建文件输入元素并触发点击事件以打开文件选择对话框
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*'; // 只允许选择图片文件
        input.onchange = async () => {
            const file = input.files?.[0];
            if (file) {
                try {
                    // 调用上传函数，这里假设 uploadFile 返回一个 Promise
                    const imageUrl = await uploadFile(file);
                    // 文件上传成功后，使用传入的回调函数插入图片链接
                    view.dispatch({
                        changes: {
                            from: main.from,
                            to: main.to,
                            insert: `![](${imageUrl})`,
                        },
                        selection: EditorSelection.range(main.from + 4, main.to + 4),
                        // selection: { anchor: main.from + 4 },
                    });
                } catch (error) {
                    console.error('文件上传失败', error);
                    // 这里可以添加错误提示给用户
                }
            }
        };
        input.click();
    },
}
export const codeBlock2: ICommand = {
    ...codeBlock,
    icon: <CodeIcon fontSize="small" />,
    execute: ({ state, view }) => {
        if (!state || !view) return;
        const main = view.state.selection.main;
        const txt = view.state.sliceDoc(view.state.selection.main.from, view.state.selection.main.to);
        view.dispatch({
            changes: {
                from: main.from,
                to: main.to,
                insert: `\`\`\`python\n${txt}\n\`\`\``,
            },
            selection: EditorSelection.range(main.from + 3, main.from + 9),
        });
    },
}