import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import "./Login.css";

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [loginType, setLoginType] = useState("");
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();

    if (username === "admin" && password === "admin123") {
      setLoginType("admin");
      setShowModal(true);
    } else if (username === "user" && password === "user123") {
      setLoginType("user");
      setShowModal(true);
    } else {
      alert("Invalid credentials! ");
    }
  };

  const handleContinue = () => {
    setShowModal(false);
    if (loginType === "admin") navigate("/admin");
    else if (loginType === "user") navigate("/user");
  };

  return (
    <div
      className="login-container"
      style={{
        backgroundImage:
          "url('https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=1400&q=80')",
      }}
    >
      <div className="overlay"></div>

      <motion.div
        className="login-box"
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <h2>Lab Occupation Portal</h2>
        <p className="subtitle">Login to continue</p>

        <form onSubmit={handleLogin}>
          <input
            type="text"
            placeholder="Enter Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

          {/* Password Input with Eye Toggle */}
          <div className="password-container">
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Enter Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <span
              className="material-symbols-outlined eye-icon"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? "visibility_off" : "visibility"}
            </span>
          </div>

          <button className="login-btn" type="submit">
            Login
          </button>
        </form>
      </motion.div>

      {/* ✨ Modal Section */}
      <AnimatePresence>
        {showModal && (
          <motion.div
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="modal-box"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              transition={{ duration: 0.4 }}
            >
              <h3>Welcome, {loginType === "admin" ? "Admin 👑" : "User 👋"}</h3>
              <p>
                You have successfully logged in to the{" "}
                {loginType === "admin" ? "Admin Dashboard" : "User Portal"}.
              </p>
              <button className="continue-btn" onClick={handleContinue}>
                Continue
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default Login;
