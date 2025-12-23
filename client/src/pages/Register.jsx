import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import Input from "../components/Input";
import Button from "../components/Button";
import "./Register.css";

export default function Register() {
  const [form, setForm] = useState({
    email: "",
    username: "",
    first_name: "",
    last_name: "",
    password: "",
    phone_number: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.post("/register", {
        ...form,
        phone_number: Number(form.phone_number),
      });
      navigate("/login");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-container">
      <div className="register-form-wrapper">
        <div className="register-header">
          <div className="register-icon-circle">
            <svg
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#667eea"
              strokeWidth="2"
            >
              <path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M12.5 11a4 4 0 100-8 4 4 0 000 8zM23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" />
            </svg>
          </div>
          <h2 className="register-title">Create Account</h2>
          <p className="register-subtitle">Join us today</p>
        </div>

        <form onSubmit={handleSubmit} className="register-form">
          {error && (
            <div className="register-error-banner">
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              {error}
            </div>
          )}

          <div className="register-row">
            <Input
              name="first_name"
              label="First Name"
              placeholder="John"
              onChange={handleChange}
              required
            />
            <Input
              name="last_name"
              label="Last Name"
              placeholder="Doe"
              onChange={handleChange}
              required
            />
          </div>

          <Input
            name="username"
            label="Username"
            placeholder="johndoe"
            onChange={handleChange}
            required
          />

          <Input
            name="email"
            label="Email"
            type="email"
            placeholder="john@example.com"
            onChange={handleChange}
            required
          />

          <Input
            name="phone_number"
            label="Phone Number"
            type="tel"
            placeholder="1234567890"
            onChange={handleChange}
            required
          />

          <Input
            name="password"
            label="Password"
            type="password"
            placeholder="••••••••"
            onChange={handleChange}
            required
          />

          <Button type="submit" fullWidth loading={loading}>
            Create Account
          </Button>
        </form>

        <div className="register-footer">
          <p className="register-footer-text">
            Already have an account?{" "}
            <span onClick={() => navigate("/login")} className="register-link">
              Sign in
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}