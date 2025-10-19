// 格式化日期字符串，使其更易读
export const formatDateTime = (isoString: string) => {
  const date = new Date(isoString);
  return date.toLocaleString(); // 根据用户本地时间格式化
};