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