// import { loadPyodide, type PyodideInterface } from "pyodide";
// import { useState, useEffect } from 'react';

// type PyodideErrorType = 'js' | 'python' | null;

// const usePyodide = () => {
//   const [isLoaded, setIsLoaded] = useState(false);
//   const [isRunning, setIsRunning] = useState(false);
//   const [pyodide, setPyodide] = useState<PyodideInterface | null>(null);
//   const [output, setOutput] = useState<string>("");
//   const [error, setError] = useState<string | null>(null);
//   const [errorType, setErrorType] = useState<PyodideErrorType>(null);

//   useEffect(() => {
//     let isCancelled = false;

//     const load = async () => {
//       try {
//         // 清除之前的状态
//         setError(null);
//         setErrorType(null);
//         setOutput("");

//         const py = await loadPyodide();
//         if (!isCancelled) {
//           setPyodide(py);
//           setIsLoaded(true);
//         }
//       } catch (err) {
//         if (isCancelled) return;
//         const message = err instanceof Error ? err.message : String(err);
//         setError(`Failed to load Pyodide: ${message}`);
//         setErrorType('js');
//         console.error('Pyodide loading error (JS):', err);
//       }
//     };

//     load();

//     return () => {
//       isCancelled = true;
//     };
//   }, []);

//   const runPython = async (code: string) => {
//     if (!pyodide) {
//       const msg = 'Pyodide is not loaded.';
//       setError(msg);
//       setErrorType('js');
//       throw new Error(msg);
//     }

//     setIsRunning(true);
//     setError(null);
//     setErrorType(null);
//     setOutput("");

//     try {
//       const result = await pyodide.runPythonAsync(code);
//       setOutput(result?.toString() || "");
//     } catch (err) {
//       // Pyodide 将 Python 异常包装为普通 Error，但可通过内容判断
//       // 实际上，所有 runPythonAsync 抛出的错误都可视为“Python 运行时错误”
//       const message = err instanceof Error ? err.message : String(err);
//       setError(message);
//       setErrorType('python');
//       console.error('Python execution error:', err);
//     } finally {
//       setIsRunning(false);
//     }
//   };

//   return {
//     isLoaded,
//     isRunning,
//     output,
//     error,
//     errorType, // 'js' | 'python' | null
//     runPython,
//   };
// };

// export default usePyodide;