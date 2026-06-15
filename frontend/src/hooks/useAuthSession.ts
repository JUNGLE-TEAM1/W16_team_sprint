import { FormEvent, useEffect, useState } from "react";

import { SESSION_STORAGE_KEY } from "../api";
import { fetchCurrentUser, logout, submitAuth } from "../services/boardApi";
import type { AuthForm, AuthMode, CurrentUser, TokenResponse } from "../types";

type UseAuthSessionOptions = {
  setError: (message: string | null) => void;
};

export function useAuthSession({ setError }: UseAuthSessionOptions) {
  const [session, setSession] = useState<TokenResponse | null>(() => {
    const rawSession = localStorage.getItem(SESSION_STORAGE_KEY);
    return rawSession ? (JSON.parse(rawSession) as TokenResponse) : null;
  });
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [authMode, setAuthMode] = useState<AuthMode>("login");
  const [authForm, setAuthForm] = useState<AuthForm>({
    email: "member@sprint.local",
    password: "password123",
  });
  const [showAuthPanel, setShowAuthPanel] = useState(false);
  const [savingAuth, setSavingAuth] = useState(false);

  const authActionLabel = authMode === "login" ? "로그인" : "가입";

  function saveSession(nextSession: TokenResponse | null) {
    setSession(nextSession);
    if (nextSession) {
      localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(nextSession));
    } else {
      localStorage.removeItem(SESSION_STORAGE_KEY);
    }
  }

  async function loadCurrentUser(nextSession = session) {
    if (!nextSession) {
      setCurrentUser(null);
      return;
    }

    try {
      setCurrentUser(await fetchCurrentUser(nextSession.access_token));
    } catch {
      saveSession(null);
      setCurrentUser(null);
    }
  }

  useEffect(() => {
    void loadCurrentUser();
  }, []);

  async function handleAuthSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSavingAuth(true);
    setError(null);
    try {
      const tokens = await submitAuth(authMode, authForm);
      saveSession(tokens);
      await loadCurrentUser(tokens);
      setShowAuthPanel(false);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "로그인 처리를 실패했습니다.");
    } finally {
      setSavingAuth(false);
    }
  }

  async function handleLogout() {
    if (session) {
      await logout(session.access_token).catch(() => undefined);
    }
    saveSession(null);
    setCurrentUser(null);
  }

  return {
    authActionLabel,
    authForm,
    authMode,
    currentUser,
    handleAuthSubmit,
    handleLogout,
    savingAuth,
    session,
    setAuthForm,
    setAuthMode,
    setShowAuthPanel,
    showAuthPanel,
  };
}
