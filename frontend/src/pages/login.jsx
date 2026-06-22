import { useState } from "react";
import { useNavigate, Navigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { API_BASE_URL } from "../config/api";
import logo from "../assets/logo.png";

const DEMO_EMAIL = "demo@xflow.local";
const DEMO_PASSWORD = "xflow1234";
const DEMO_USER = {
  user_id: "demo-user",
  email: DEMO_EMAIL,
  name: "데모 사용자",
  is_admin: true,
  role_id: null,
  etl_access: true,
  domain_edit_access: true,
  dataset_access: [],
  all_datasets: true,
  role_dataset_etl_access: true,
  role_query_ai_access: true,
};

function Login() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const { login, sessionId } = useAuth();

  // Redirect to dashboard if already logged in
  if (sessionId) {
    return <Navigate to="/demo/realtime-alerts" replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      if (
        import.meta.env.DEV &&
        formData.email.trim().toLowerCase() === DEMO_EMAIL &&
        formData.password === DEMO_PASSWORD
      ) {
        login(`demo-session-${Date.now()}`, DEMO_USER);
        navigate("/demo/realtime-alerts");
        return;
      }

      const response = await fetch(`${API_BASE_URL}/api/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        alert(data.detail || "Login failed");
        return;
      }

      login(data.session_id, data.user);

      // Redirect based on permissions
      if (data.user.is_admin || data.user.etl_access) {
        navigate("/dataset");
      } else {
        navigate("/catalog");
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Login failed. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <img src={logo} alt="AskLake" className="h-16 w-auto object-contain mx-auto mb-3" />
          {/* Description */}
          <p className="text-gray-600">AI 데이터 플랫폼</p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-lg shadow-xl p-8 border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            로그인
          </h2>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                이메일
              </label>
              <input
                id="email"
                name="email"
                required
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                placeholder="demo@xflow.local"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                비밀번호
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className={`w-full py-3 px-4 rounded-lg font-medium transition ${isSubmitting
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                } text-white`}
            >
              {isSubmitting ? "로그인 중..." : "로그인"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
export default Login;
