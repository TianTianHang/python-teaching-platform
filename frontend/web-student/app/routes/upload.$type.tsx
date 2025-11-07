import { withAuth } from "~/utils/loaderWrapper";
import type { Route } from "./+types/upload.$type";


import { redirect } from "react-router";
import { fileServices } from "~/localstorage.server";
import { destroySession, getSession } from "~/sessions.server";


export const action = withAuth(async ({ request, params }: Route.ActionArgs) => {
    const session = await getSession(request.headers.get('Cookie'));
    if (!session.get("isAuthenticated")) {
        return redirect(`/auth/login`, {
            headers: {
                "Set-Cookie": await destroySession(session),
            },
        });
    }

    const userId = session.get("user")?.id || 1;
    if (!userId) {
        return Response.json({ error: "User ID missing" }, { status: 400 });
    }



    // 构造逻辑 key，例如 "user-123"
    const logicalKey = `user-${userId}`;

    // 定义上传处理器：只处理字段名为 "avatar" 的文件
    const uploadHandler = async (fileUpload: File) => {
        console.log("handle file upload")
        const service = fileServices().get(params.type+"s");
        if (!service) {
            throw new Error(`${params.type} file service not configured`);
        }
        try {
            // 上传并返回公开 URL（如 /files/avatars/user-123.jpg）
            return await service.upload(logicalKey, fileUpload);
        } catch (error) {
            console.error("Upload failed:", error);
            throw new Response("Invalid file", { status: 400 });
        }
    };
    const formData = await request.formData()
    const file = formData.get(params.type);

    if (!file || !(file instanceof File)) {
        return Response.json({ error: "No valid avatar file provided" }, { status: 400 });
    }
    const url= await uploadHandler(file);

    if (!url || typeof url !== "string") {
        return Response.json({ error: "Upload failed: no file returned" }, { status: 400 });
    }


    return { success: true, url };
});


// export default function Component({ actionData }: Route.ComponentProps) {
//     return (
//         <div>
//             <form method="post" encType="multipart/form-data" action="/upload/avatar">
//                 <input type="file" name="avatar" />
//                 <button>Submit</button>
//             </form>
//             <img src={actionData?.url} />
//         </div>

//     );
// }