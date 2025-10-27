import type { User } from "./user";

export interface Course {
  id: number;
  title: string;
  description: string;
  created_at: string; // ISO 8601
  updated_at: string;
}

export interface Chapter {
  id: number;
  course_title: string; 
  title: string;
  content: string;
  order: number;
  created_at: string;
  updated_at: string;
}

export interface Problem{
  id:number;
  type:"algorithm"|string;
  title:string;
  content:string;
  chapter_title?:string;
  difficulty:number;
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
  enrolled_at:string;
  last_accessed_at:string; 
  progress_percentage:number;
}