import type { Thread } from "./thread";

export interface Course {
  id: number;
  title: string;
  description: string;
  recent_threads:Thread[]
  created_at: string; // ISO 8601
  updated_at: string;
}

export interface Chapter {
  id: number;
  course_title: string;
  title: string;
  content: string;
  order: number;
  status: "not_started"|"in_progress"|"completed"
  created_at: string;
  updated_at: string;
  unlock_condition?: ChapterUnlockCondition;
  is_locked: boolean;
  prerequisite_progress?: PrerequisiteProgress;
}

// 前置章节摘要（后端返回的简化对象）
export interface PrerequisiteChapterSummary {
  id: number;
  title: string;
  order: number;
  course_title?: string;
}

export interface ChapterUnlockCondition {
  id: number;
  unlock_condition_type: 'prerequisite' | 'date' | 'all';
  unlock_date: string | null;
  prerequisite_chapters?: PrerequisiteChapterSummary[];
  prerequisite_chapter_ids?: number[];
}
export type ProblemStatus='not_started'|'in_progress'|'solved'|'failed';

export interface PrerequisiteProblem {
  id: number;
  title: string;
  difficulty: number;
}

export interface PrerequisiteProgress {
  total: number;
  completed: number;
  remaining: PrerequisiteChapterSummary[];
}

export interface UnlockConditionDescription {
  type: string; // 'prerequisite' | 'date' | 'both' | 'none'
  type_display: string;
  is_prerequisite_required: boolean;
  is_date_required: boolean;
  prerequisite_problems: PrerequisiteProblem[];
  unlock_date: string | null; // ISO 8601 format
  has_conditions: boolean;
  prerequisite_count?: number;
}

// Task 5.2: Add unlock status response type
export interface ChapterUnlockStatus {
  is_locked: boolean;
  reason?: 'prerequisite' | 'date' | 'both' | null;
  prerequisite_progress: PrerequisiteProgress | null;
  unlock_date?: string | null;
  time_until_unlock?: {
    days: number;
    hours: number;
    minutes: number;
  };
}

export interface Problem{
  id:number;
  type:"algorithm"|string;
  title:string;
  content:string;
  chapter_title?:string;
  difficulty:number;
  status: ProblemStatus;
  is_unlocked: boolean;
  unlock_condition_description: UnlockConditionDescription;
  recent_threads: Thread[];
  created_at:string;
  updated_at: string;
}
export interface Template{
  python:string;
}
export interface AlgorithmProblem extends Problem{
  type: "algorithm";
  time_limit:number;
  memory_limit:number;
  code_template:Template;
  solution_name: Template;
  sample_cases:TestCase[];
}
export type ProgrssStatue ='not_started'|'in_progress'|'solved'|'failed'
export interface ProblemProgress{
  id:number;
  enrollment:number;
  problem: number;
  problem_title: string;
  problem_type: string;
  problem_difficulty: number;
  chapter_title:string;
  course_title:string;
  status:ProgrssStatue;
  attempts:number;
  last_attempted_at:string;
  solved_at:string;
  best_submission:string;
}
export interface ChoiceProblem extends Problem{
  options:Record<string,string>;
  correct_answer:string|string[];
  is_multiple_choice:boolean;
}

export interface BlankAnswer {
  id: string; // 'blank1', 'blank2', etc.
  answers: string[];
  case_sensitive: boolean;
}

export interface FillBlankResult {
  user_answer: string;
  is_correct: boolean;
  correct_answers: string[];
}

export interface CheckFillBlankResponse {
  all_correct: boolean;
  results: Record<string, FillBlankResult>;
}

export interface FillBlankProblem extends Problem {
  type: "fillblank";
  content_with_blanks: string;
  blanks: { blanks?: BlankAnswer[] | string[]; case_sensitive?: boolean };
  blanks_list: BlankAnswer[];
  blank_count: number;
}
export interface TestCase{
  input_data:string;
  expected_output:string;
  is_sample:boolean;
  created_at:string;
}
export interface Enrollment{
  id:number;
  user:number;
  user_username:string;
  course:number;
  course_title:string;
  next_chapter:Chapter;
  enrolled_at:string;
  last_accessed_at:string;
  progress_percentage:number;
}

// ============================================================================
// 测验功能相关类型定义
// ============================================================================

export interface Exam {
  id: number;
  course: number;
  course_title: string;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  total_score: number;
  passing_score: number;
  status: "draft" | "published" | "archived";
  shuffle_questions: boolean;
  show_results_after_submit: boolean;
  created_at: string;
  updated_at: string;
  exam_problems: ExamProblem[];
  is_active: boolean;
  question_count: number;
  remaining_time:{
    remaining_seconds:number;
    deadline:string;
  }
  user_submission_status?: {
    status: 'in_progress' | 'submitted' | 'auto_submitted' | 'graded';
    submitted_at?: string;
    total_score?: number;
    is_passed?: boolean;
  };
}

export interface ExamProblem {
  exam_problem_id: number;
  problem_id: number;
  title: string;
  content: string;
  type: "choice" | "fillblank";
  difficulty: number;
  score: number;
  order: number;
  options?: Record<string, string>; // 选择题选项
  is_multiple_choice?: boolean; // 选择题是否多选
  content_with_blanks?: string; // 填空题内容
  blanks_list?: BlankAnswer[]; // 填空题列表
  blank_count?: number; // 填空题数量
}

export interface ExamSubmission {
  id: number;
  exam: number;
  exam_title: string;
  user: number;
  username: string;
  started_at: string;
  submitted_at?: string;
  status: "in_progress" | "submitted" | "auto_submitted" | "graded";
  total_score?: string;
  is_passed?: boolean;
  time_spent_seconds?: number;
  exam_passing_score?: number;
  exam_total_score?: number;
  answers: ExamAnswer[];
}

export interface ExamAnswer {
  id: number;
  problem: number;
  problem_title: string;
  problem_type: string;
  choice_answers?: string | string[]; // 选择题答案
  fillblank_answers?: Record<string, string>; // 填空题答案
  score?: string;
  is_correct?: boolean;
  correct_percentage?: number;
  correct_answer?: ExamAnswerCorrect;
  problem_data?: ExamAnswerProblemData;
  created_at: string;
}

export interface ExamAnswerCorrect {
  // For choice problems
  correct_answer?: string | string[];
  is_multiple?: boolean;
  all_options?: Record<string, string>;
  // For fillblank problems
  blanks_list?: BlankAnswer[];
  case_sensitive?: boolean;
}

export interface ExamAnswerProblemData {
  content: string;
  difficulty: number;
  score:number;
}