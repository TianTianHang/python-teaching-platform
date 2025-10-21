export interface CourseProgress {
  id: number;
  userId: number;
  courseId: number;
  completedChapters: number[];
  totalChapters: number;
  completionPercentage: number;
  lastAccessed: string; // ISO string
  completedAt?: string; // ISO string, optional
}

export interface ChapterProgress {
  id: number;
  userId: number;
  chapterId: number;
  isCompleted: boolean;
  completedAt?: string; // ISO string, optional
  lastAccessed: string; // ISO string
}

export interface ProgressSummary {
  completedCourses: number;
  totalCourses: number;
  currentStreak: number;
  totalStudyTime: number; // in minutes
  completedChapters: number;
  totalChapters: number;
}