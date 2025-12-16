import type { Thread } from "./thread";
import type { User } from "./user";

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
}
export type ProblemStatus='not_started'|'in_progress'|'solved'|'failed';
export interface Problem{
  id:number;
  type:"algorithm"|string;
  title:string;
  content:string;
  chapter_title?:string;
  difficulty:number;
  status: ProblemStatus;
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