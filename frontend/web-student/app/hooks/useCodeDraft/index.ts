import { useState, useEffect, useCallback, useRef } from 'react';
import { useDebounceFn } from 'ahooks';
import useFetcherAction from '~/hooks/useFetcherAction';
import { showNotification } from '~/components/Notification';
import type { SaveType, CodeDraftStorage, CodeDraft } from '~/types/codeDraft';

interface UseCodeDraftOptions {
  problemId: number;
  initialCode?: string;
  language?: string;
}

interface UseCodeDraftReturn {
  code: string;
  setCode: (code: string) => void;
  saveDraft: (saveType?: SaveType) => Promise<void>;
  isLoading: boolean;
  lastSavedAt: Date | null;
  saveType: SaveType | null;
  hasUnsavedChanges: boolean;
  // 新增：保存状态跟踪
  saveStatus: 'idle' | 'saving' | 'success' | 'error';
  saveError: Error | null;
}

export const useCodeDraft = ({
  problemId,
  initialCode = '',
  language = 'python'
}: UseCodeDraftOptions): UseCodeDraftReturn => {
  const [code, setCodeState] = useState(initialCode);
  const [isLoading, setIsLoading] = useState(false);
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null);
  const [saveType, setSaveType] = useState<SaveType | null>(null);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  // 新增：保存状态跟踪
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle');
  const [saveError, setSaveError] = useState<Error | null>(null);

  const isMounted = useRef(true);
  const lastSavedRef = useRef<CodeDraftStorage | null>(null);

  const localStorageKey = `code-draft-${problemId}-${language}`;

  // 跟踪组件挂载状态
  useEffect(() => {
    isMounted.current = true;
    return () => {
      isMounted.current = false;
    };
  }, []);

  // 页面卸载前立即保存
  useEffect(() => {
    const handleBeforeUnload = () => {
      if (hasUnsavedChanges && isMounted.current) {
        saveToLocal(code, 'auto_save');
        // 可选：也尝试保存到服务器（但不阻塞）
        const blob = new Blob(
          [JSON.stringify({ code, language, save_type: 'auto_save' })],
          { type: 'application/json' }
        );
        navigator.sendBeacon(`/api/v1/problems/${problemId}/save_draft/`, blob);
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [code, hasUnsavedChanges, problemId, language]);

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(localStorageKey);
      if (stored) {
        const draft: CodeDraftStorage = JSON.parse(stored);
        // Only use stored code if it's for the same problem and language
        if (draft.problemId === problemId && draft.language === language) {
          setCodeState(draft.code);
          setLastSavedAt(new Date(draft.savedAt));
          setSaveType(draft.saveType);
        }
      }
    } catch (error) {
      console.error('Failed to load code draft from localStorage:', error);
    }
  }, [problemId, language]);

  // Setup useFetcherAction for loading latest draft
  const loadFetcher = useFetcherAction<CodeDraft, string>({
    action: `/problems/${problemId}/latest_draft/`,
    method: 'GET', // useFetcherAction uses POST as default
    timeout: 10000,
    onSuccess: (data) => {
      if(!data) return;
      if (!isMounted.current) return;

      if (data.code) {
        const serverTime = new Date(data.created_at);
        const localTime = lastSavedAt;

        // 只有在服务器草稿更新时且没有未保存更改时才应用
        if (!hasUnsavedChanges && (!localTime || serverTime > localTime)) {
          setCodeState(data.code);
          setLastSavedAt(serverTime);
          setSaveType(data.save_type);
          setHasUnsavedChanges(false); // 清除未保存更改标志

          // 同步到 localStorage
          const storage: CodeDraftStorage = {
            code: data.code,
            problemId,
            language,
            savedAt: data.created_at,
            saveType: data.save_type
          };
          localStorage.setItem(localStorageKey, JSON.stringify(storage));
        } else {
          console.log('服务器草稿比本地版本旧，保留本地代码');
        }
      }
    },
    onError: (error) => {
      console.error('Failed to load latest draft from server:', error);
    }
  });

  // Load latest draft from server on mount
  useEffect(() => {
    loadFetcher.loader();
  }, [problemId]);

  // Save to localStorage immediately with optimization
  const saveToLocal = useCallback((
    codeToSave: string,
    type: SaveType
  ) => {
    try {
      const storage: CodeDraftStorage = {
        code: codeToSave,
        problemId,
        language,
        savedAt: new Date().toISOString(),
        saveType: type
      };

      // 只有内容变化时才写入
      if (!lastSavedRef.current ||
          lastSavedRef.current.code !== codeToSave ||
          lastSavedRef.current.saveType !== type) {
        localStorage.setItem(localStorageKey, JSON.stringify(storage));
        lastSavedRef.current = storage;
      }

      setLastSavedAt(new Date());
      setSaveType(type);
    } catch (error) {
      console.error('Failed to save code draft to localStorage:', error);
    }
  }, [problemId, language]);

  // Setup useFetcherAction for saving drafts
  const saveFetcher = useFetcherAction<CodeDraft, string>({
    action: `/problems/${problemId}/save_draft/`,
    method: 'POST',
    timeout: 10000,
    onSuccess: (data) => {
      if (!isMounted.current) return;

      // Update last saved time
      setLastSavedAt(new Date(data.created_at));
      setSaveType(data.save_type);
      setHasUnsavedChanges(false); // 保存成功后清除未保存更改标志

      // Update save status
      setSaveStatus('success');
      setSaveError(null);

      // Show success notification for manual saves
      if (isMounted.current) {
        showNotification('success', '保存成功', '代码已保存到服务器');
      }
    },
    onError: (error) => {
      console.error('Failed to save code draft to server:', error);
      setSaveStatus('error');
      const errorObj = error as unknown as Error & { message?: string };
      setSaveError(errorObj);

      // Show error notification
      if (isMounted.current) {
        showNotification('error', '保存失败', errorObj.message || '无法保存到服务器，但代码已保存到本地');
      }
      throw error;
    }
  });

  // Save to server using fetcher
  const saveToServer = useCallback(async (
    codeToSave: string,
    type: SaveType
  ) => {
    setIsLoading(true);
    try {
      saveFetcher.submit({
        code: codeToSave,
        language,
        save_type: type
      });
    } catch (error) {
      console.error('Failed to save code draft to server:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [problemId, language, saveFetcher.submit]);

  // Combined save function
  const saveDraft = useCallback(async (
    type: SaveType = 'manual_save'
  ) => {
    // Update save status
    if (type === 'manual_save') {
      setSaveStatus('saving');
      setSaveError(null);
    }

    // Always save to localStorage first (immediate)
    saveToLocal(code, type);

    // Then save to server (async, doesn't block)
    try {
      await saveToServer(code, type);
    } catch (err) {
      if (isMounted.current) {
        // Server save failed, but localStorage save succeeded
        console.warn('Server save failed, code preserved in localStorage:', err);

        // For manual saves that fail, show a different notification
        if (type === 'manual_save') {
          setTimeout(() => {
            if (isMounted.current) {
              showNotification('error', '保存失败', '代码已保存到本地，但无法保存到服务器');
            }
          }, 500);
        }
      }
    }
  }, [code, saveToLocal, saveToServer]);

  // Debounced auto-save: triggers 5 seconds after user stops editing
  const { run: debouncedAutoSave } = useDebounceFn(
    () => {
      saveDraft('auto_save');
    },
    { wait: 5000 } // 5 seconds instead of 30
  );

  // Watch for code changes and trigger debounced auto-save
  useEffect(() => {
    debouncedAutoSave();
  }, [code, debouncedAutoSave]);

  // Simple setCode that updates state and triggers debounced auto-save
  const setCode = useCallback((newCode: string) => {
    setCodeState(newCode);
    setHasUnsavedChanges(true); // 标记为有未保存的更改
    // Auto-save will be triggered by the debounced watcher above
  }, []);

  return {
    code,
    setCode,
    saveDraft,
    isLoading,
    lastSavedAt,
    saveType,
    hasUnsavedChanges,
    saveStatus,
    saveError,
  };
};