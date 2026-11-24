"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { clearAuth, getStoredUser, getToken, type AuthUser } from "@/lib/api";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    setUser(getStoredUser());
  }, [router]);

  function logout() {
    clearAuth();
    router.replace("/login");
  }

  return (
    <div className="cc-shell">
      <aside className="cc-sidebar" aria-label="Primary navigation">
        <div className="cc-brand">CARE<span>CIRCLE</span></div>
        <nav className="cc-nav">
          <Link href="/family">Dashboard</Link>
          <Link href="/family/parents">My Parents</Link>
        </nav>
        <div className="cc-account">
          {user ? (
            <>
              <div><strong>{user.full_name}</strong></div>
              <button type="button" className="cc-button secondary" onClick={logout} style={{ marginTop: 10, width: "100%" }}>
                Sign out
              </button>
            </>
          ) : null}
        </div>
      </aside>
      <main className="cc-main">
        <div className="cc-container">{children}</div>
      </main>
    </div>
  );
}
