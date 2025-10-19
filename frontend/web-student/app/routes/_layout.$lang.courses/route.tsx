import type { Page } from "~/types/page";
import type { Route } from "./+types/route";
import type { Course } from "~/types/course";
import http from "~/utils/http";
import CourseList from "./components/CourseList";

// export  async function loader({ params,request }: Route.LoaderArgs) {
  
//   const courses = await http.get<Page<Course>>("courses");
//   return courses;
// }
export  async function clientLoader({ params }: Route.ClientLoaderArgs) {
  const courses = await http.get<Page<Course>>("courses");
  return courses;
}



export default function CoursePage({params, loaderData}:Route.ComponentProps) {
  return <>
    <CourseList courses={loaderData.results} lang={params.lang}/>
  </>
}