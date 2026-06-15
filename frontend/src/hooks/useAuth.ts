import { useState } from "react";
import type { FormEvent } from "react";

import type {
  AuthFormState,
  AuthView,
  FieldChangeEvent,
  LoadOptions,
  LoginResponse,
  User,
} from "../types";
import type { ApiRequest } from "./useApiRequest";

interface UseAuthOptions {
  request: ApiRequest;
}

export function useAuth({ request }: UseAuthOptions) {
  const [authView, setAuthView] = useState<AuthView>(null);
  const [authForm, setAuthForm] = useState<AuthFormState>({
    username: "team1",
    password: "password123",
    display_name: "Team One",
  });
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  function showLogin() {
    setAuthView("login");
  }

  function showRegister() {
    setAuthView("register");
  }

  function hideAuth() {
    setAuthView(null);
  }

  function updateAuthForm(event: FieldChangeEvent) {
    setAuthForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  }

  async function register(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const result = await request<User>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(authForm),
      successMessage: "계정 생성 완료. 로그인해주세요.",
    });
    if (result.ok) {
      showLogin();
    }
    return result.ok;
  }

  async function login(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const result = await request<LoginResponse>("/api/v1/auth/session/login", {
      method: "POST",
      body: JSON.stringify({
        username: authForm.username,
        password: authForm.password,
      }),
      successMessage: "로그인되었습니다.",
    });
    if (result.ok) {
      setCurrentUser(result.data.user);
      hideAuth();
    }
    return result.ok;
  }

  async function loadMe(options: LoadOptions = {}) {
    const result = await request<User>("/api/v1/auth/session/me", {
      quiet: options.quiet,
      successMessage: "현재 사용자 정보를 확인했습니다.",
    });
    if (result.ok) {
      setCurrentUser(result.data);
      return result.data;
    }
    return null;
  }

  async function logout() {
    const result = await request<Record<string, never>>("/api/v1/auth/session/logout", {
      method: "POST",
      successMessage: "로그아웃되었습니다.",
    });
    if (result.ok) {
      setCurrentUser(null);
      hideAuth();
    }
    return result.ok;
  }

  return {
    authView,
    authForm,
    currentUser,
    showLogin,
    showRegister,
    hideAuth,
    updateAuthForm,
    register,
    login,
    loadMe,
    logout,
  };
}
