import { create } from "zustand";

interface GlobalState{
    markdownStyle:any
}

export const useGolbalStore =create<GlobalState>()((set, get) => ({
        markdownStyle: {
        '& h1, & h2, & h3, & h4, & h5, & h6': { mt: 3, mb: 1 },
        '& p': { mb: 2 },
        '& ul, & ol': { ml: 4, mb: 2 },
        '& a': {
            color: 'primary.main',
            textDecoration: 'none',
            '&:hover': { textDecoration: 'underline' },
        },
        '& code': {
            backgroundColor: '#f2f2f2',
            padding: '2px 4px',
            borderRadius: '4px',
            fontFamily: 'monospace',
        },
        '& pre': {
            backgroundColor: '#2d2d2d',
            color: '#f8f8f2',
            padding: '16px',
            borderRadius: '8px',
            overflowX: 'auto',
            margin: '24px 0',
        },
        '& pre code': {
            backgroundColor: 'transparent',
            padding: 0,
            borderRadius: 0,
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
        },
    }
}))

