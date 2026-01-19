/**
 * 代码草稿类型定义
 */

export type SaveType = 'auto_save' | 'manual_save' | 'submission';

export interface CodeDraft {
  id: number;
  user: number;
  username: string;
  problem: number;
  problem_title: string;
  code: string;
  language: string;
  save_type: SaveType;
  submission_id?: number;
  created_at: string;
  updated_at: string;
}

export interface CodeDraftStorage {
  code: string;
  problemId: number;
  language: string;
  savedAt: string;
  saveType: SaveType;
}

export interface SaveDraftRequest {
  problem_id: number;
  code: string;
  language?: string;
  save_type?: SaveType;
  submission_id?: number;
}
