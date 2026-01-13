import { useOutletContext } from "react-router";
import type { User } from "~/types/user";
export type UserContextType = { user: User | null }
export function useUser() {
  return useOutletContext<UserContextType>();
}