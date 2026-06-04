export interface Course {
  id: number;
  title: string;
  description?: string;
  subject?: string;
  teacher_name?: string;
}

export interface RuntimeInfo {
  llm_mode: string;
  mock_mode: boolean;
}
