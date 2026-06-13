import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import type { UserResponse } from "@/lib/types";
import { clearToken, setOnUnauthorized, setToken } from "@/lib/api";

interface AuthState {
  user: UserResponse | null;
  login: (user: UserResponse, token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

function parseToken(token: string): { sub: string; exp: number } | null {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload;
  } catch {
    return null;
  }
}

function restoreUser(): UserResponse | null {
  const token = localStorage.getItem("koffeeza_token");
  if (!token) return null;

  const parsed = parseToken(token);
  if (!parsed || parsed.exp * 1000 <= Date.now()) {
    clearToken();
    localStorage.removeItem("koffeeza_user");
    return null;
  }

  const stored = localStorage.getItem("koffeeza_user");
  if (!stored) {
    clearToken();
    return null;
  }

  try {
    return JSON.parse(stored) as UserResponse;
  } catch {
    clearToken();
    localStorage.removeItem("koffeeza_user");
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(restoreUser);

  const logout = useCallback(() => {
    clearToken();
    localStorage.removeItem("koffeeza_user");
    setUser(null);
  }, []);

  useEffect(() => {
    setOnUnauthorized(logout);
  }, [logout]);

  const login = useCallback((u: UserResponse, token: string) => {
    setToken(token);
    localStorage.setItem("koffeeza_user", JSON.stringify(u));
    setUser(u);
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
