"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { BrainCircuit, Lock, Mail, User, ArrowRight, Eye, EyeOff } from "lucide-react";
import { api } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [name, setName] = useState("Admin User");
  const [email, setEmail] = useState("admin@retainiq.com");
  const [password, setPassword] = useState("password123");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (mode === "signup") {
        await api.post("/auth/register", {
          name,
          email,
          password,
        });
      }

      const res = await api.post<{ access_token: string }>("/auth/login", {
        email,
        password,
      });

      if (res.access_token) {
        localStorage.setItem("retainiq_token", res.access_token);
        router.push("/dashboard");
      }
    } catch (err: any) {
      if (err.message === "Failed to fetch") {
        setError("Unable to connect to backend server. Please make sure FastAPI backend is running on http://localhost:8000.");
      } else {
        setError(err.message || "Failed to authenticate. Please check your details.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-slate-950 p-4">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl">
        <div className="flex flex-col items-center mb-6 text-center">
          <div className="p-3 bg-indigo-600 rounded-xl text-white mb-3 shadow-lg shadow-indigo-500/20">
            <BrainCircuit className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold text-white">RetainIQ Platform</h1>
          <p className="text-sm text-slate-400 mt-1">
            {mode === "signin" ? "Sign in to your account" : "Create a new analyst account"}
          </p>
        </div>

        {/* Tab Toggle */}
        <div className="grid grid-cols-2 bg-slate-950 p-1 rounded-xl border border-slate-800 mb-6">
          <button
            type="button"
            onClick={() => {
              setMode("signin");
              setError(null);
            }}
            className={`py-2 text-xs font-semibold rounded-lg transition-all ${
              mode === "signin"
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => {
              setMode("signup");
              setError(null);
            }}
            className={`py-2 text-xs font-semibold rounded-lg transition-all ${
              mode === "signup"
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Sign Up
          </button>
        </div>

        {error && (
          <div className="mb-6 p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400 text-sm leading-relaxed">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === "signup" && (
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Full Name
              </label>
              <div className="relative">
                <User className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Rahul Sharma"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2.5 pl-10 pr-4 text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@retainiq.com"
                className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2.5 pl-10 pr-4 text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type={showPassword ? "text" : "password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2.5 pl-10 pr-10 text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                title={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2.5 rounded-lg text-sm transition-colors flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/25 disabled:opacity-50 mt-2"
          >
            {loading
              ? mode === "signin"
                ? "Signing in..."
                : "Creating Account..."
              : mode === "signin"
              ? "Sign In"
              : "Create Account"}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-6 text-center text-xs text-slate-400">
          {mode === "signin" ? (
            <p>
              Don&apos;t have an account?{" "}
              <button
                type="button"
                onClick={() => {
                  setMode("signup");
                  setError(null);
                }}
                className="text-indigo-400 hover:underline font-semibold"
              >
                Sign Up
              </button>
            </p>
          ) : (
            <p>
              Already have an account?{" "}
              <button
                type="button"
                onClick={() => {
                  setMode("signin");
                  setError(null);
                }}
                className="text-indigo-400 hover:underline font-semibold"
              >
                Sign In
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
