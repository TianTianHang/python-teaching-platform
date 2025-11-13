import type { UploadImgCallBack } from "md-editor-rt";
import { showNotification } from "~/components/Notification";

export async function uploadFile(file:File,type:string) {
    const formData = new FormData();
    formData.append(type, file);

    // 这里的 '/upload' 是你的服务器接收文件上传的接口地址
    const response = await fetch(`/upload/${type}`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        throw new Error('网络响应异常');
    }

    const data = await response.json();
    // 假设服务器返回的数据结构包含图片的URL
    return data.url as string;
}

export const handleUpload = async (files: File[], callback: UploadImgCallBack) => {
    const res = await Promise.all(
      files.map((file) => {
        return uploadFile(file, "thread")
      })
    );
    showNotification("success", "上传成功", "图片成功上传")
    callback(res);
  }