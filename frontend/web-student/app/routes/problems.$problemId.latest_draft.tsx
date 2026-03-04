import { useParams } from "react-router";
import { clientHttp } from "~/utils/http/client";
import { useState, useEffect } from "react";

export default function useLatestDraft() {
    const { problemId } = useParams();
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<any>(null);
    
    useEffect(() => {
        if (!problemId) return;
        
        const fetchData = async () => {
            setLoading(true);
            try {
                const result = await clientHttp.get(`/drafts/latest/`, {
                    problem_id: parseInt(problemId)
                });
                setData(result);
            } catch (error: any) {
                if (error?.response?.status === 404) {
                    setData(null);
                } else {
                    console.error(error);
                }
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [problemId]);
    
    return { data, loading };
}