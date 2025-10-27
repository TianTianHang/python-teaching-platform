export interface Page<T> {
  count: number;
  next: string | null; //下一页链接
  previous: string | null; //上一页链接
  page_size?:number;
  results: T[];
}