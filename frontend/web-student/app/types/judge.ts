export  interface CodeExecutionRequest {
  code: string;
  language: string;
  input?: string;
}

export interface CodeExecutionResponse {
  output: string;
  error?: string;
  executionTime?: number;
  success: boolean;
}

export interface ChapterWithExercises {
  id: number;
  title: string;
  content: string;
  course_title: string;
  order: number;
  created_at: string;
  updated_at: string;
  exercises?: Exercise[];
}

export interface Exercise {
  id: number;
  title: string;
  description: string;
  starterCode: string;
  testCases: TestCase[];
  difficulty: 'easy' | 'medium' | 'hard';
}

export interface TestCase {
  id: number;
  input: string;
  expectedOutput: string;
  isHidden: boolean;
}

